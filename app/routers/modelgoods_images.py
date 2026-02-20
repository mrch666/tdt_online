from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam, String, LargeBinary
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

        # Получаем текущее значение imgext (может быть NULL или пустое)
        current_result = db.execute(
            text("""
                SELECT FIRST 1 "imgext"
                FROM "modelgoods"
                WHERE "id" = :modelid
            """),
            {"modelid": modelid}
        ).fetchone()
        
        current_imgext = current_result[0] if current_result and current_result[0] else None

        # Формируем имя файла с новым расширением (временно)
        # Получаем числовые части ID
        id_parts_result = db.execute(
            text("""
                SELECT FIRST 1
                    DEC64I0(MG."id"),
                    DEC64I1(MG."id")
                FROM "modelgoods" MG
                WHERE MG."id" = :modelid
            """),
            {"modelid": modelid}
        ).fetchone()

        if not id_parts_result:
            raise HTTPException(500, "Cannot get ID parts for filename generation")

        part0 = id_parts_result[0]
        part1 = id_parts_result[1]
        filename = f"{part0}_{part1}.{imgext}"
        img_path = os.path.join(os.getenv('BASE_DIR'), os.getenv('IMG_SUBDIR')) + os.sep

        try:
            file_data = await file.read()
            
            # Подробное логирование параметров
            logger.debug(f"Stored procedure parameters:")
            logger.debug(f"  - img_path: {img_path} (type: {type(img_path)})")
            logger.debug(f"  - filename: {filename} (type: {type(filename)})")
            logger.debug(f"  - file_data length: {len(file_data)} bytes (type: {type(file_data)})")
            logger.debug(f"  - file_data first 100 bytes: {file_data[:100]}")
            
            # Проверяем типы параметров
            # Параметры должны быть строкой, строкой и байтами
            param1 = str(img_path)  # Убедимся, что это строка
            param2 = str(filename)  # Убедимся, что это строка
            param3 = bytes(file_data)  # Убедимся, что это байты
            
            logger.debug(f"Converted parameters:")
            logger.debug(f"  - param1 (img_path): {param1} (type: {type(param1)})")
            logger.debug(f"  - param2 (filename): {param2} (type: {type(param2)})")
            logger.debug(f"  - param3 (file_data): <binary data {len(param3)} bytes> (type: {type(param3)})")
            
            # Используем позиционные параметры (?, ?, ?) - передаем как кортеж параметров
            # Тестирование показало, что позиционные параметры работают
            logger.debug(f"Executing stored procedure: SELECT * FROM \"wp_SaveBlobToFile\"(?, ?, ?)")
            logger.debug(f"With parameters: ({param1}, {param2}, <binary data {len(param3)} bytes>)")
            
            # Выполняем хранимую процедуру с позиционными параметрами
            # Используем text() с bindparams для явного указания типов параметров
            stmt = text("SELECT * FROM \"wp_SaveBlobToFile\"(:p1, :p2, :p3)")
            
            # Явно указываем типы параметров через bindparams
            stmt = stmt.bindparams(
                bindparam("p1", value=param1, type_=String),
                bindparam("p2", value=param2, type_=String),
                bindparam("p3", value=param3, type_=LargeBinary)
            )
            
            db.execute(stmt, {"p1": param1, "p2": param2, "p3": param3})
            db.commit()
            logger.info(f"Image saved via stored procedure: {filename}")
                
        except Exception as e:
            db.rollback()
            logger.error(f"Stored procedure error: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details'}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(500, f"File save failed: {str(e)}")
        finally:
            await file.close()

        # Только после успешного сохранения файла обновляем БД
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