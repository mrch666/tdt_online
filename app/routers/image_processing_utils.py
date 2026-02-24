"""
Утилиты для оптимизированной обработки изображений
"""
import logging
import tempfile
import os
from fastapi import UploadFile, HTTPException
import io
from sqlalchemy.orm import Session
from sqlalchemy import text
import requests
from PIL import Image
import asyncio

logger = logging.getLogger("api")

def is_jpg_file(filename: str) -> bool:
    """
    Проверяет, является ли файл JPG/JPEG
    
    Args:
        filename: Имя файла
        
    Returns:
        True если файл JPG/JPEG, иначе False
    """
    if not filename:
        return False
    
    file_extension = filename.lower().split('.')[-1].split('?')[0]
    return file_extension in ['jpg', 'jpeg']

def save_jpg_directly(content: bytes, file_path: str) -> str:
    """
    Сохраняет JPG файл напрямую без конвертации через Pillow
    
    Args:
        content: Байтовое содержимое файла
        file_path: Путь для сохранения файла
        
    Returns:
        Путь к сохраненному файлу
    """
    try:
        with open(file_path, 'wb') as f:
            f.write(content)
        logger.info(f"JPG файл сохранен напрямую: {file_path}, размер: {len(content)} байт")
        return file_path
    except Exception as e:
        logger.error(f"Ошибка при сохранении JPG файла: {str(e)}")
        raise

async def process_image_directly(
    modelid: str,
    image_content: bytes,
    filename: str,
    db: Session
):
    """
    Обрабатывает изображение напрямую, без HTTP запроса
    
    Args:
        modelid: ID модели товара
        image_content: Байтовое содержимое изображения
        filename: Имя файла
        db: Сессия базы данных
        
    Returns:
        Результат обработки
    """
    from .modelgoods_images import upload_model_image
    
    try:
        # Создаем UploadFile из байтов
        upload_file = UploadFile(
            filename=filename,
            file=io.BytesIO(image_content)
        )
        
        # Вызываем upload_model_image напрямую
        result = await upload_model_image(
            modelid=modelid,
            file=upload_file,
            db=db
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при прямой обработке изображения: {str(e)}")
        raise

def download_image_with_optimization(url: str):
    """
    Скачивает изображение с оптимизацией для JPG файлов
    
    Args:
        url: URL изображения
        
    Returns:
        Кортеж (содержимое файла, имя файла)
        
    Raises:
        HTTPException: Если не удалось скачать изображение
    """
    try:
        logger.info(f"Скачивание изображения с URL: {url}")
        
        # Скачиваем изображение
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Получаем имя файла из URL
        filename = url.split('/')[-1].split('?')[0]
        if not filename:
            filename = "image.jpg"
        
        content = response.content
        content_length = len(content)
        
        logger.info(f"Скачано изображение: {filename}, размер: {content_length} байт")
        
        if content_length == 0:
            raise HTTPException(status_code=400, detail="Пустое изображение")
        
        return content, filename
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при скачивании изображения: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Ошибка при скачивании изображения: {str(e)}")
    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Ошибка при обработке изображения: {str(e)}")

async def optimize_external_image_processing(
    modelid: str,
    image_url: str,
    db: Session
) -> dict:
    """
    Оптимизированная обработка внешнего изображения
    
    Args:
        modelid: ID модели товара
        image_url: URL изображения
        db: Сессия базы данных
        
    Returns:
        Словарь с результатом обработки
    """
    try:
        # 1. Скачиваем изображение
        image_content, filename = download_image_with_optimization(image_url)
        
        # 2. Проверяем, является ли файл JPG
        if is_jpg_file(filename):
            logger.info(f"Файл {filename} является JPG, используем оптимизированную обработку")
            
            # 3. Обрабатываем напрямую
            result = await process_image_directly(
                modelid=modelid,
                image_content=image_content,
                filename=filename,
                db=db
            )
            
            return {
                "status": "success",
                "message": "Изображение успешно обработано (оптимизированный путь)",
                "result": result.dict() if hasattr(result, 'dict') else result
            }
        else:
            logger.info(f"Файл {filename} не JPG, используем стандартную обработку")
            # Для не-JPG файлов нужно использовать существующую логику
            # с конвертацией через Pillow
            raise HTTPException(
                status_code=400,
                detail=f"Файл {filename} не поддерживается для оптимизированной обработки"
            )
            
    except HTTPException as e:
        logger.error(f"Ошибка HTTP при обработке изображения: {e.detail}")
        return {
            "status": "error",
            "message": f"Ошибка обработки изображения: {e.detail}"
        }
    except Exception as e:
        logger.error(f"Неожиданная ошибка при оптимизированной обработке: {str(e)}")
        return {
            "status": "error",
            "message": f"Внутренняя ошибка сервера: {str(e)}"
        }