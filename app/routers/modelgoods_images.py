from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import os
import json
from typing import Optional

from app.database import get_db
from app.schemas.modelgoods_images import ImageUploadResponse, ImageInfo, ImageDeleteResponse

logger = logging.getLogger("api")
router = APIRouter(prefix="/modelgoods/image", tags=["modelgoods_images"])

@router.post("/", response_model=ImageUploadResponse)
async def upload_model_image(
    modelid: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Загрузка изображения для товара
    """
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
            
            # Пробуем вызвать хранимую процедуру с позиционными параметрами
            # Тестирование показало, что процедура ожидает 3 параметра в определенном порядке
            # и работает только с позиционными параметрами (?), а не с именованными
            try:
                # Важно: путь должен заканчиваться на \ для правильной конкатенации в процедуре
                if not img_path.endswith('\\'):
                    img_path = img_path + '\\'
                
                # Вызываем процедуру с позиционными параметрами
                result = db.execute(
                    text("SELECT * FROM \"wp_SaveBlobToFile\"(?, ?, ?)"),
                    [img_path, filename, file_data]
                )
                db.commit()
                
                # Проверяем результат
                proc_result = result.fetchone()
                if proc_result and len(proc_result) > 0:
                    # Первое поле в результате - это код результата (1 = успех)
                    success = proc_result[0]
                    if success == 1:
                        logger.info(f"File saved via stored procedure: {filename}, result: {success}")
                    else:
                        logger.warning(f"Stored procedure returned error code: {success}")
                        # Не прерываем выполнение, т.к. есть fallback
                        raise Exception(f"Procedure returned error code: {success}")
                else:
                    logger.warning("Stored procedure returned no result")
                    raise Exception("No result from procedure")
                    
            except Exception as proc_error:
                # Если процедура не работает, сохраняем файл напрямую через файловую систему
                db.rollback()
                logger.warning(f"Stored procedure failed: {proc_error}. Saving file directly...")
                
                # Создаем полный путь к файлу
                full_path = os.path.join(img_path.rstrip('\\'), filename)
                
                # Создаем директорию, если она не существует
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Сохраняем файл
                with open(full_path, 'wb') as f:
                    f.write(file_data)
                
                logger.info(f"File saved directly: {full_path}")
                
        except Exception as e:
            db.rollback()
            logger.error(f"File save error: {str(e)}")
            raise HTTPException(500, "File save failed")
        finally:
            await file.close()

        db.execute(
            text("""
                UPDATE "modelgoods" 
                SET "imgext" = :imgext, 
                    "changedate" = CURRENT_TIMESTAMP 
                WHERE "id" = :modelid
            """),
            {"imgext": imgext, "modelid": modelid}
        )
        db.commit()

        return ImageUploadResponse(status="success", filename=filename)
        
    except Exception as e:
        logger.error(f"Image upload error: {str(e)}")
        raise HTTPException(500, "Internal server error")


@router.get("/{modelid}", response_model=ImageInfo)
async def get_model_image_info(
    modelid: str,
    db: Session = Depends(get_db)
):
    """
    Получение информации об изображении товара
    """
    try:
        result = db.execute(
            text("""
                SELECT FIRST 1 
                    MG."id" as modelid,
                    DEC64I0(MG."id") || '_' || DEC64I1(MG."id") || '.' || MG."imgext" as filename,
                    MG."imgext",
                    MG."changedate"
                FROM "modelgoods" MG 
                WHERE MG."id" = :modelid
            """),
            {"modelid": modelid}
        ).fetchone()
        
        if not result:
            raise HTTPException(404, "Model not found")
            
        if not result[1]:  # filename is empty
            raise HTTPException(404, "Image not found for this model")
            
        return ImageInfo(
            modelid=result[0],
            filename=result[1],
            imgext=result[2],
            changedate=str(result[3]) if result[3] else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get image info error: {str(e)}")
        raise HTTPException(500, "Internal server error")


@router.delete("/{modelid}", response_model=ImageDeleteResponse)
async def delete_model_image(
    modelid: str,
    db: Session = Depends(get_db)
):
    """
    Удаление изображения товара
    """
    try:
        # Получаем информацию о файле
        result = db.execute(
            text("""
                SELECT FIRST 1 
                    DEC64I0(MG."id") || '_' || DEC64I1(MG."id") || '.' || MG."imgext" as filename
                FROM "modelgoods" MG 
                WHERE MG."id" = :modelid
            """),
            {"modelid": modelid}
        ).fetchone()
        
        if not result or not result[0]:
            raise HTTPException(404, "Model not found or no image")
            
        filename = result[0]
        img_path = os.path.join(os.getenv('BASE_DIR'), os.getenv('IMG_SUBDIR'))

        # Удаляем файл через хранимую процедуру
        try:
            # Важно: путь должен заканчиваться на \ для правильной конкатенации в процедуре
            if not img_path.endswith('\\'):
                img_path = img_path + '\\'
            
            # Для процедуры wp_DeleteFile нужно 2 позиционных параметра
            result = db.execute(
                text("SELECT * FROM \"wp_DeleteFile\"(?, ?)"),
                [img_path, filename]
            )
            db.commit()
            
            # Проверяем результат
            proc_result = result.fetchone()
            if proc_result and len(proc_result) > 0:
                success = proc_result[0]
                if success == 1:
                    logger.info(f"File deleted via stored procedure: {filename}, result: {success}")
                else:
                    logger.warning(f"Delete procedure returned error code: {success}")
                    # Не прерываем выполнение, просто логируем
        except Exception as e:
            db.rollback()
            logger.error(f"File delete error: {str(e)}")
            # Если не удалось удалить файл, все равно обновляем запись
            db.execute(
                text(""" 
                    UPDATE "modelgoods" 
                    SET "imgext" = NULL, 
                        "changedate" = CURRENT_TIMESTAMP 
                    WHERE "id" = :modelid
                """),
                {"modelid": modelid}
            )
            db.commit()
            return ImageDeleteResponse(
                status="warning", 
                message=f"File delete failed but record cleared: {str(e)}"
            )
        
        # Обновляем запись в БД
        db.execute(
            text("""
                UPDATE "modelgoods" 
                SET "imgext" = NULL, 
                    "changedate" = CURRENT_TIMESTAMP 
                WHERE "id" = :modelid
            """),
            {"modelid": modelid}
        )
        db.commit()
        
        return ImageDeleteResponse(
            status="success", 
            message="Image deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete image error: {str(e)}")
        raise HTTPException(500, "Internal server error")