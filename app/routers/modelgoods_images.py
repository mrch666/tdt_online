from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import os
import json
import tempfile
import zipfile

from app.database import get_db

logger = logging.getLogger("api")
router = APIRouter(prefix="/modelgoods/image", tags=["modelgoods_images"])

def save_description_to_file(product_id: str, desc: str, db: Session):
    product_id = product_id.strip()
    if not product_id or not desc:
        raise HTTPException(400, "Invalid product ID or description")
    
    try:
     if product_id and desc:
        desc = str(desc).strip(' ').replace('&amp;mdash;', "-")
        desc=desc.replace('\n',"<br>\n")
        desc = f'<div>{desc}</div>'
        print(desc)
        sql="""SELECT * FROM \"wp_SaveBlobToFile\"('C:\\Program Files (x86)\\tdt3\\bases\\desc\\', dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.dat',:zip_file)"""
        print(sql)
        #dec_id = decModelID(product_id)
        obj_zip = tempfile.TemporaryFile(delete=False)
        try:
            zip_path_temp = obj_zip.name
            with zipfile.ZipFile(zip_path_temp, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                zip_file.writestr('desc.txt', desc)

            with open(zip_path_temp, 'rb') as zip_file:
                db.execute(text(sql), {'modelid':product_id,"zip_file": zip_file}).fetchall()
            db.commit()
            db.execute(text("""UPDATE "modelgoods" SET "changedate"=current_timestamp where "id"=:id"""), {"id": product_id})
            db.commit()
            print("Успешно записали описание", product_id)
        except Exception as e:
            print(f'Не удалось записать описание товара {product_id}',e)
        finally:
            obj_zip.close()
        
        return {"status": "success"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving description: {str(e)}")
        raise HTTPException(500, "Description save failed")

@router.post("/")
async def upload_model_image(
    modelid: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        imgext = file.filename.split('.')[-1].split('?')[0]
        
        result = db.execute(
            text("""
                SELECT FIRST 1 
                    DEC64I0(MG."id") || '_' || DEC64I1(MG."id") || '.' || MG."imgext" 
                FROM "modelgoods" MG 
                WHERE MG."id" = :modelid
            """),
            {"modelid": modelid}
        ).fetchone()
        
        if not result or not result[0]:
            raise HTTPException(404, "Model not found")
            
        filename = result[0].split('?')[0]
        img_path = os.path.join(os.getenv('BASE_DIR'), os.getenv('IMG_SUBDIR'))

        try:
            file_data = await file.read()
            db.execute(
                text("SELECT * FROM wp_SaveBlobToFile(:path, :filename, :data)"),
                {
                    "path": img_path,
                    "filename": filename,
                    "data": file_data
                }
            )
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"File save error: {str(e)}")
            raise HTTPException(500, "File save failed")
        finally:
            await file.close()

        db.execute(
            text("""
                UPDATE modelgoods 
                SET imgext = :imgext, 
                    changedate = CURRENT_TIMESTAMP 
                WHERE id = :modelid
            """),
            {"imgext": imgext, "modelid": modelid}
        )
        db.commit()

        return {"status": "success", "filename": filename}
        
    except Exception as e:
        logger.error(f"Image upload error: {str(e)}")
        raise HTTPException(500, "Internal server error")

class DescriptionInput(BaseModel):
    description: str

@router.post("/description/{modelid}")
async def upload_model_description(
    request: Request,
    modelid: str,  # modelid из URL пути
    data: DescriptionInput,  # автоматическая валидация JSON тела
    db: Session = Depends(get_db)
):
    try:
               
        return save_description_to_file(modelid, data.description, db)
        
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON format")
    except Exception as e:
        logger.error(f"Description upload error: {str(e)}")
        raise HTTPException(500, "Internal server error")
