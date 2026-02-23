from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text, and_
import logging
from typing import List, Optional
import aiohttp
import asyncio
from PIL import Image
import io
import re

from app.database import get_db
from app.models import ModelgoodsExternalImages, Modelgoods
from app.schemas.modelgoods_external_images import (
    ExternalImageCreate,
    ExternalImageUpdate,
    ExternalImageResponse,
    ExternalImageListResponse,
    ExternalImageStatusResponse,
    ImageValidationRequest,
    ImageValidationResponse
)

logger = logging.getLogger("api")
router = APIRouter(prefix="/api/modelgoods/external-images", tags=["modelgoods_external_images"])


async def check_image_url(url: str) -> dict:
    """
    Проверка доступности и размеров изображения по URL
    """
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return {
                        "is_valid": False,
                        "message": f"Не удалось загрузить изображение. Код ответа: {response.status}",
                        "details": {"status_code": response.status}
                    }
                
                # Проверка Content-Type
                content_type = response.headers.get('Content-Type', '').lower()
                if 'image/jpeg' not in content_type and 'image/jpg' not in content_type:
                    return {
                        "is_valid": False,
                        "message": f"Неправильный тип контента. Ожидается image/jpeg, получено: {content_type}",
                        "details": {"content_type": content_type}
                    }
                
                # Читаем первые 2MB для проверки размеров
                max_size = 2 * 1024 * 1024  # 2MB
                chunk = await response.content.read(max_size)
                
                if not chunk:
                    return {
                        "is_valid": False,
                        "message": "Изображение пустое или не удалось прочитать данные",
                        "details": {"size": 0}
                    }
                
                # Проверяем размеры через Pillow
                try:
                    image = Image.open(io.BytesIO(chunk))
                    width, height = image.size
                    
                    if width < 399 or height < 299:
                        return {
                            "is_valid": False,
                            "message": f"Размер изображения слишком мал: {width}x{height}. Минимум 400x300",
                            "details": {"width": width, "height": height}
                        }
                    
                    return {
                        "is_valid": True,
                        "message": f"Изображение валидно. Размер: {width}x{height}",
                        "details": {"width": width, "height": height, "size": len(chunk)}
                    }
                    
                except Exception as img_error:
                    return {
                        "is_valid": False,
                        "message": f"Ошибка при обработке изображения: {str(img_error)}",
                        "details": {"error": str(img_error)}
                    }
                    
    except asyncio.TimeoutError:
        return {
            "is_valid": False,
            "message": "Таймаут при загрузке изображения",
            "details": {"timeout": True}
        }
    except Exception as e:
        return {
            "is_valid": False,
            "message": f"Ошибка при проверке URL: {str(e)}",
            "details": {"error": str(e)}
        }


@router.post("/validate", response_model=ImageValidationResponse)
async def validate_external_image(
    request: ImageValidationRequest
):
    """
    Валидация внешнего изображения по URL
    """
    try:
        validation_result = await check_image_url(request.url)
        
        return ImageValidationResponse(
            is_valid=validation_result["is_valid"],
            message=validation_result["message"],
            details=validation_result.get("details")
        )
        
    except Exception as e:
        logger.error(f"Ошибка валидации изображения: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при валидации изображения: {str(e)}"
        )


@router.post("/", response_model=ExternalImageResponse, status_code=status.HTTP_201_CREATED)
async def create_external_image(
    image_data: ExternalImageCreate,
    db: Session = Depends(get_db)
):
    """
    Добавление ссылки на внешнее изображение для товара
    """
    try:
        # Проверяем существование товара
        model_exists = db.query(Modelgoods).filter(
            Modelgoods.id == image_data.modelid
        ).first()
        
        if not model_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товар с ID {image_data.modelid} не найден"
            )
        
        # Проверяем валидность URL
        validation_result = await check_image_url(image_data.url)
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result["message"]
            )
        
        # Создаем новую запись
        db_image = ModelgoodsExternalImages(
            modelid=image_data.modelid,
            url=image_data.url,
            userid=image_data.userid or "0",
            is_approved=0,
            is_loaded_to_db=0
        )
        
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        # Преобразуем в схему ответа
        response_data = ExternalImageResponse(
            id=db_image.id,
            modelid=db_image.modelid,
            url=db_image.url,
            userid=db_image.userid,
            is_approved=db_image.is_approved,
            is_loaded_to_db=db_image.is_loaded_to_db,
            created_at=db_image.created_at,
            updated_at=db_image.updated_at
        )
        
        logger.info(f"Добавлена ссылка на внешнее изображение: ID={db_image.id}, ModelID={db_image.modelid}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при добавлении внешнего изображения: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при добавлении изображения: {str(e)}"
        )


@router.get("/{modelid}", response_model=ExternalImageListResponse)
async def get_external_images_by_model(
    modelid: str,
    is_approved: Optional[int] = Query(None, ge=0, le=1, description="Фильтр по статусу одобрения"),
    is_loaded_to_db: Optional[int] = Query(None, ge=0, le=1, description="Фильтр по статусу загрузки в БД"),
    db: Session = Depends(get_db)
):
    """
    Получение всех ссылок на внешние изображения для товара
    """
    try:
        # Проверяем существование товара
        model_exists = db.query(Modelgoods).filter(
            Modelgoods.id == modelid
        ).first()
        
        if not model_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товар с ID {modelid} не найден"
            )
        
        # Строим запрос с фильтрами
        query = db.query(ModelgoodsExternalImages).filter(
            ModelgoodsExternalImages.modelid == modelid
        )
        
        if is_approved is not None:
            query = query.filter(ModelgoodsExternalImages.is_approved == is_approved)
        
        if is_loaded_to_db is not None:
            query = query.filter(ModelgoodsExternalImages.is_loaded_to_db == is_loaded_to_db)
        
        # Получаем результаты
        images = query.order_by(ModelgoodsExternalImages.created_at.desc()).all()
        
        # Преобразуем в схему ответа
        response_images = []
        for image in images:
            response_images.append(ExternalImageResponse(
                id=image.id,
                modelid=image.modelid,
                url=image.url,
                userid=image.userid,
                is_approved=image.is_approved,
                is_loaded_to_db=image.is_loaded_to_db,
                created_at=image.created_at,
                updated_at=image.updated_at
            ))
        
        return ExternalImageListResponse(
            images=response_images,
            total=len(response_images)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении внешних изображений: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении изображений: {str(e)}"
        )


@router.put("/{image_id}", response_model=ExternalImageStatusResponse)
async def update_external_image_status(
    image_id: str,
    update_data: ExternalImageUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновление статусов внешнего изображения
    """
    try:
        # Находим изображение
        db_image = db.query(ModelgoodsExternalImages).filter(
            ModelgoodsExternalImages.id == image_id
        ).first()
        
        if not db_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Изображение с ID {image_id} не найдено"
            )
        
        # Обновляем только переданные поля
        update_fields = {}
        if update_data.is_approved is not None:
            update_fields["is_approved"] = update_data.is_approved
        
        if update_data.is_loaded_to_db is not None:
            update_fields["is_loaded_to_db"] = update_data.is_loaded_to_db
        
        if update_fields:
            for field, value in update_fields.items():
                setattr(db_image, field, value)
            
            db.commit()
            db.refresh(db_image)
            
            logger.info(f"Обновлены статусы изображения {image_id}: {update_fields}")
            
            return ExternalImageStatusResponse(
                id=image_id,
                status="success",
                message="Статусы успешно обновлены"
            )
        else:
            return ExternalImageStatusResponse(
                id=image_id,
                status="no_changes",
                message="Нет изменений для обновления"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при обновлении статусов изображения: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении статусов: {str(e)}"
        )


@router.delete("/{image_id}", response_model=ExternalImageStatusResponse)
async def delete_external_image(
    image_id: str,
    db: Session = Depends(get_db)
):
    """
    Удаление ссылки на внешнее изображение
    """
    try:
        # Находим изображение
        db_image = db.query(ModelgoodsExternalImages).filter(
            ModelgoodsExternalImages.id == image_id
        ).first()
        
        if not db_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Изображение с ID {image_id} не найдено"
            )
        
        # Удаляем запись
        db.delete(db_image)
        db.commit()
        
        logger.info(f"Удалена ссылка на внешнее изображение: ID={image_id}")
        
        return ExternalImageStatusResponse(
            id=image_id,
            status="success",
            message="Ссылка на изображение успешно удалена"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при удалении внешнего изображения: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении изображения: {str(e)}"
        )


@router.get("/", response_model=ExternalImageListResponse)
async def get_all_external_images(
    modelid: Optional[str] = Query(None, min_length=12, max_length=12, description="Фильтр по ID товара"),
    is_approved: Optional[int] = Query(None, ge=0, le=1, description="Фильтр по статусу одобрения"),
    is_loaded_to_db: Optional[int] = Query(None, ge=0, le=1, description="Фильтр по статусу загрузки в БД"),
    limit: int = Query(100, ge=1, le=1000, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: Session = Depends(get_db)
):
    """
    Получение всех ссылок на внешние изображения с фильтрами
    """
    try:
        # Строим запрос с фильтрами
        query = db.query(ModelgoodsExternalImages)
        
        if modelid:
            query = query.filter(ModelgoodsExternalImages.modelid == modelid)
        
        if is_approved is not None:
            query = query.filter(ModelgoodsExternalImages.is_approved == is_approved)
        
        if is_loaded_to_db is not None:
            query = query.filter(ModelgoodsExternalImages.is_loaded_to_db == is_loaded_to_db)
        
        # Получаем общее количество
        total = query.count()
        
        # Получаем результаты с пагинацией
        images = query.order_by(
            ModelgoodsExternalImages.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Преобразуем в схему ответа
        response_images = []
        for image in images:
            response_images.append(ExternalImageResponse(
                id=image.id,
                modelid=image.modelid,
                url=image.url,
                userid=image.userid,
                is_approved=image.is_approved,
                is_loaded_to_db=image.is_loaded_to_db,
                created_at=image.created_at,
                updated_at=image.updated_at
            ))
        
        return ExternalImageListResponse(
            images=response_images,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Ошибка при получении всех внешних изображений: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении изображений: {str(e)}"
        )