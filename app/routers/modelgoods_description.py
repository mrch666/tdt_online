from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import tempfile
import zipfile
import json

from app.database import get_db

logger = logging.getLogger("api")
router = APIRouter(
    prefix="/modelgoods/description",
    tags=["modelgoods_description"],
    responses={404: {"description": "Не найдено"}},
)

class DescriptionInput(BaseModel):
    description: str

def save_description_to_file(product_id: str, desc: str, db: Session):
    product_id = product_id.strip()
    if not product_id or not desc:
        raise HTTPException(400, "Invalid product ID or description")
    
    try:
        if product_id and desc:
            desc = str(desc).strip(' ').replace('&mdash;', "-")
            desc = desc.replace('\n',"<br>\n")
            desc = f'<div>{desc}</div>'
            sql = """SELECT * FROM \"wp_SaveBlobToFile\"('C:\\Program Files (x86)\\tdt3\\bases\\desc\\', dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.dat',:zip_file)"""
            
            obj_zip = tempfile.TemporaryFile(delete=False)
            try:
                zip_path_temp = obj_zip.name
                with zipfile.ZipFile(zip_path_temp, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    zip_file.writestr('desc.txt', desc)

                with open(zip_path_temp, 'rb') as zip_file:
                    db.execute(text(sql), {'modelid': product_id, "zip_file": zip_file}).fetchall()
                db.commit()
                db.execute(text("""UPDATE "modelgoods" SET "changedate"=current_timestamp where "id"=:id"""), {"id": product_id})
                db.commit()
            except Exception as e:
                raise HTTPException(500, f"Failed to save description: {str(e)}")
            finally:
                obj_zip.close()
            
            return {"status": "success"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving description: {str(e)}")
        raise HTTPException(500, "Description save failed")

@router.post(
    "/{modelid}",
    summary="Сохранение текстового описания товара",
    response_description="Результат сохранения описания",
    responses={
        200: {"description": "Описание успешно сохранено"},
        400: {"description": "Неверный формат данных"},
        500: {"description": "Ошибка сервера при сохранении"},
    },
)
async def upload_model_description(
    request: Request,
    modelid: str,
    data: DescriptionInput,
    db: Session = Depends(get_db)
):
    try:
        return save_description_to_file(modelid, data.description, db)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON format")
    except Exception as e:
        logger.error(f"Description upload error: {str(e)}")
        raise HTTPException(500, "Internal server error")
