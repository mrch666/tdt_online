from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
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
        desc = desc.strip().replace('&mdash;', "-")
        desc = desc.replace('\n', "<br>\n")
        desc_html = f'<div>{desc}</div>'
        
        sql = text("""SELECT * FROM "wp_SaveBlobToFile"(
            :base_path, 
            dec64i0(:product_id) || '_' || dec64i1(:product_id) || :ext, 
            :zip_data
        )""")
        
        base_path = os.path.join(os.getenv('BASE_DIR'), os.getenv('DESC_SUBDIR'))
        
        with tempfile.TemporaryFile() as tmp_file:
            with zipfile.ZipFile(tmp_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr('desc.txt', desc_html)
            
            tmp_file.seek(0)
            zip_data = tmp_file.read()
        
        db.execute(sql, {
            "base_path": base_path,
            "product_id": product_id,
            "ext": ".dat",
            "zip_data": zip_data
        })
        db.commit()
        
        db.execute(text("""UPDATE "modelgoods" SET "changedate"=current_timestamp WHERE "id"=:id"""), 
                 {"id": product_id})
        db.commit()
        
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

@router.post("/description/")
async def upload_model_description(
    request: Request,
    modelid: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        content = await request.json()
        if "description" not in content:
            raise HTTPException(400, "Description field is required")
        
        return save_description_to_file(modelid, content["description"], db)
        
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON format")
    except Exception as e:
        logger.error(f"Description upload error: {str(e)}")
        raise HTTPException(500, "Internal server error")
