from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import os
import json
import tempfile
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

        # Сначала проверяем существование товара
        result = db.execute(
            text("""
                SELECT FIRST 1 "id"
                FROM "modelgoods"
                WHERE "id" = :modelid
            """),
            {"modelid": modelid}
        ).fetchone()

        if not result:
            raise HTTPException(404, "Model not found")

        # Обновляем поле imgext в БД ДО сохранения файла
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

        # Теперь получаем правильное имя файла с расширением
        result = db.execute(
            text("""
                SELECT FIRST 1
                    DEC64I0(MG."id") || '_' || DEC64I1(MG."id") || '.' || MG."imgext"
                FROM "modelgoods" MG
                WHERE MG."id" = :modelid
            """),
            {"modelid": modelid}
        ).fetchone()

        filename = result[0].split('?')[0] if result and result[0] else f"{modelid}.{imgext}"
        img_path = os.path.join(os.getenv('BASE_DIR'), os.getenv('IMG_SUBDIR')) + os.sep

        try:
            file_data = await file.read()
            
            # Используем позиционные параметры (?, ?, ?) - это работает!
            # Именованные параметры (:path, :filename, :data) не работают
            db.execute(
                text("SELECT * FROM \"wp_SaveBlobToFile\"(?, ?, ?)"),
                [img_path, filename, file_data]
            )
            db.commit()
            
            logger.info(f"Image saved via stored procedure: {filename}")
                
        except Exception as e:
            db.rollback()
            logger.error(f"Stored procedure error: {str(e)}")
            raise HTTPException(500, f"File save failed: {str(e)}")
        finally:
            await file.close()

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
        img_path = os.path.join(os.getenv('BASE_DIR'), os.getenv('IMG_SUBDIR')) + os.sep

        # Удаляем файл через хранимую процедуру
        try:
            # Формируем SQL запрос аналогично загрузке описаний
            sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', '{filename}')"""
            db.execute(text(sql))
            db.commit()
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