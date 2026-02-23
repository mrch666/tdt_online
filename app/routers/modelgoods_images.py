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

# Helper functions to decode model IDs
def dec64i0(modelid: str) -> str:
    """Decode first part of model ID"""
    return modelid[:8]

def dec64i1(modelid: str) -> str:
    """Decode second part of model ID"""
    return modelid[8:16]

@router.post("/", response_model=ImageUploadResponse)
async def upload_model_image(
    modelid: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Загрузка изображения для товара с использованием временного файла
    """
    try:
        # Логируем длину modelid для отладки
        logger.debug(f"Получен modelid: '{modelid}'")
        logger.debug(f"Длина modelid: {len(modelid)} символов")
        
        if len(modelid) != 12:
            logger.warning(f"ВНИМАНИЕ: modelid имеет длину {len(modelid)} вместо 12 символов!")
        
        imgext = file.filename.split('.')[-1].split('?')[0]

        # Сначала проверяем существование товара
        logger.debug(f"Выполняем проверку существования товара с modelid: '{modelid}'")
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

        # Формируем имя файла
        filename = f"{dec64i0(modelid)}_{dec64i1(modelid)}.{imgext}"
        img_path = os.path.join(os.getenv('BASE_DIR'), os.getenv('IMG_SUBDIR')) + os.sep

        try:
            # Читаем данные файла
            file_data = await file.read()
            
            logger.debug(f"Загрузка изображения:")
            logger.debug(f"  - img_path: {img_path}")
            logger.debug(f"  - filename: {filename}")
            logger.debug(f"  - file_data length: {len(file_data)} bytes")
            
            # Проверяем существование старого файла и удаляем его
            full_path = os.path.join(img_path, filename)
            if os.path.exists(full_path):
                old_size = os.path.getsize(full_path)
                logger.info(f"Старый файл существует, размер: {old_size} байт")
                
                # Пробуем удалить через хранимую процедуру
                try:
                    delete_sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', '{filename}')"""
                    db.execute(text(delete_sql))
                    db.commit()
                    logger.info(f"Старый файл удален через хранимую процедуру: {filename}")
                    
                    # Даем время на удаление
                    import time
                    time.sleep(1)
                    
                    # Проверяем удаление
                    if os.path.exists(full_path):
                        logger.warning(f"Файл все еще существует после удаления через процедуру")
                        # Пробуем удалить еще раз с большей задержкой
                        time.sleep(2)
                except Exception as delete_error:
                    logger.warning(f"Не удалось удалить старый файл через процедуру: {delete_error}")
                    # Пробуем удалить напрямую (хотя скорее всего не получится из-за прав)
                    try:
                        os.unlink(full_path)
                        logger.info(f"Старый файл удален напрямую: {filename}")
                    except Exception as direct_delete_error:
                        logger.warning(f"Не удалось удалить старый файл напрямую: {direct_delete_error}")
                
                # Даем дополнительное время на освобождение файла
                import time
                time.sleep(2)
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
                tmp_file.write(file_data)
                tmp_path = tmp_file.name
            
            tmp_size = os.path.getsize(tmp_path)
            logger.debug(f"Временный файл создан: {tmp_path}, размер: {tmp_size} байт")
            
            # Выполняем хранимую процедуру через временный файл
            # Используем bindparam с явным указанием типа BLOB
            from sqlalchemy import bindparam, LargeBinary, String
            
            sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.' || :imgext, :file_content)""")
            
            # Создаем bindparam с явным указанием типа LargeBinary (BLOB)
            sql = sql.bindparams(
                bindparam('dir', type_=String),
                bindparam('modelid', type_=String),
                bindparam('imgext', type_=String),
                bindparam('file_content', type_=LargeBinary)
            )
            
            logger.debug(f"Выполняемый SQL: {sql}")
            
            with open(tmp_path, 'rb') as tmp_file:
                file_blob = tmp_file.read()
            
            logger.debug(f"Передаваемые данные: {len(file_blob)} байт")
            
            # Создаем параметры
            params = {
                'dir': img_path,
                'modelid': modelid,
                'imgext': imgext,
                'file_content': file_blob
            }
            
            # Выполняем запрос с явным указанием типа для BLOB
            result = db.execute(sql, params).fetchall()
            
            db.commit()
            
            logger.info(f"Изображение сохранено через временный файл: {filename}")
            logger.info(f"Результат процедуры: {result}")
            
            # Проверяем сохраненный файл
            import time
            time.sleep(1)  # Даем время на сохранение
            
            if os.path.exists(full_path):
                saved_size = os.path.getsize(full_path)
                logger.info(f"Файл сохранен: {full_path}, размер: {saved_size} байт")
                
                if saved_size != len(file_data):
                    logger.error(f"ВНИМАНИЕ: Размер сохраненного файла ({saved_size}) не совпадает с переданными данными ({len(file_data)})")
                    # Проверяем содержимое
                    try:
                        with open(full_path, 'rb') as f:
                            saved_data = f.read()
                        if saved_data != file_data:
                            logger.error(f"ВНИМАНИЕ: Содержимое сохраненного файла не совпадает с переданными данными")
                            logger.error(f"Первые 20 байт сохраненного: {saved_data[:20]}")
                            logger.error(f"Первые 20 байт переданных: {file_data[:20]}")
                    except Exception as read_error:
                        logger.error(f"Ошибка при проверке содержимого файла: {read_error}")
                else:
                    logger.info(f"OK: Размер сохраненного файла совпадает с переданными данными")
            else:
                logger.error(f"ВНИМАНИЕ: Файл не сохранен: {full_path}")
                raise HTTPException(500, "File was not saved on server")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Ошибка сохранения изображения: {str(e)}")
            logger.error(f"Тип ошибки: {type(e)}")
            import traceback
            logger.error(f"Трассировка: {traceback.format_exc()}")
            raise HTTPException(500, f"File save failed: {str(e)}")
        finally:
            await file.close()
            # Удаляем временный файл
            try:
                os.unlink(tmp_path)
                logger.debug(f"Временный файл удален: {tmp_path}")
            except Exception as unlink_error:
                logger.warning(f"Не удалось удалить временный файл: {unlink_error}")

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