from fastapi import APIRouter, Depends, HTTPException, Request, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import os
import logging
import tempfile
import zipfile
import json
import io
import re

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
            desc_dir = os.path.join(os.getenv('BASE_DIR'), os.getenv('DESC_SUBDIR')) + os.sep
            sql = f"""SELECT * FROM \"wp_SaveBlobToFile\"('{desc_dir}', dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.dat',:zip_file)"""
            
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

def get_model_description_sync(modelid: str, db: Session) -> Optional[str]:
    try:
        result = db.execute(
            text("""
                SELECT loadblobfromfile(
                    :desc_dir || dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.dat'
                ) as dat 
                FROM "modelgoods" 
                WHERE "id" = :modelid
            """),
            {
                "modelid": modelid,
                "desc_dir": os.path.join(os.getenv('BASE_DIR'), os.getenv('DESC_SUBDIR')) + os.sep
            }
        ).fetchone()

        if not result or not result[0]:
            return None

        zip_data = io.BytesIO(result[0])
        description = None
        
        with zipfile.ZipFile(zip_data, "r") as zip_file:
            for filename in zip_file.namelist():
                try:
                    with zip_file.open(filename, 'r') as f:
                        content = f.read()
                        
                        # Try UTF-8 decoding first
                        try:
                            text_content = content.decode('utf-8')
                        except UnicodeDecodeError:
                            text_content = content.decode('cp1251')
                            
                        # Clean HTML tags and attributes
                        cleaned_content = re.sub(r'(class|id)=".*?"', '', text_content)
                        cleaned_content = re.sub(r'<form[\s\S]+?</form>', '', cleaned_content)
                        
                        if cleaned_content.strip():
                            description = cleaned_content
                            break
                            
                except Exception as e:
                    logger.error(f"Ошибка чтения файла {filename}: {str(e)}")
                    continue
                    
        return description

    except Exception as e:
        logger.error(f"Ошибка получения описания: {str(e)}")
        return None

@router.get(
    "/{modelid}",
    summary="Получение текстового описания товара",
    response_description="Текст описания товара",
    responses={
        200: {"description": "Описание успешно получено"},
        404: {"description": "Описание не найдено"},
        500: {"description": "Ошибка сервера при получении"},
    },
)
async def get_model_description(
    modelid: str,
    db: Session = Depends(get_db),
):
    description = get_model_description_sync(modelid, db)
    if not description:
        raise HTTPException(404, "Описание не найдено")
    return {"description": description}

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
