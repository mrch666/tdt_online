from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List
from datetime import datetime
import re


class ExternalImageBase(BaseModel):
    """Базовая схема для внешних изображений"""
    modelid: str = Field(..., min_length=12, max_length=12, description="ID товара (12 символов)")
    url: str = Field(..., max_length=2000, description="URL изображения")
    userid: Optional[str] = Field("0", max_length=12, description="ID пользователя")


class ExternalImageCreate(ExternalImageBase):
    """Схема для создания записи о внешнем изображении"""
    
    @validator('url')
    def validate_url(cls, v):
        """Валидация URL"""
        # Проверка формата URL
        if not re.match(r'^https?://', v, re.IGNORECASE):
            raise ValueError('URL должен начинаться с http:// или https://')
        
        # # Проверка расширения файла (только jpg/jpeg)
        # url_lower = v.lower()
        # if not (url_lower.endswith('.jpg') or url_lower.endswith('.jpeg')):
        #     raise ValueError('Поддерживаются только изображения формата JPG/JPEG')
        
        return v


class ExternalImageUpdate(BaseModel):
    """Схема для обновления статусов изображения"""
    is_approved: Optional[int] = Field(None, ge=0, le=1, description="Статус одобрения (0/1)")
    is_loaded_to_db: Optional[int] = Field(None, ge=0, le=1, description="Статус загрузки в БД (0/1)")


class ExternalImageResponse(ExternalImageBase):
    """Схема для ответа API"""
    id: str = Field(..., max_length=12, description="ID записи")
    is_approved: int = Field(..., ge=0, le=1, description="Статус одобрения (0/1)")
    is_loaded_to_db: int = Field(..., ge=0, le=1, description="Статус загрузки в БД (0/1)")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    
    class Config:
        from_attributes = True


class ExternalImageListResponse(BaseModel):
    """Схема для списка изображений"""
    images: List[ExternalImageResponse] = Field(..., description="Список изображений")
    total: int = Field(..., description="Общее количество изображений")


class ExternalImageStatusResponse(BaseModel):
    """Схема для ответа об изменении статуса"""
    id: str = Field(..., max_length=12, description="ID записи")
    status: str = Field(..., description="Статус операции")
    message: str = Field(..., description="Сообщение")


class ImageValidationRequest(BaseModel):
    """Схема для запроса валидации изображения"""
    url: str = Field(..., max_length=2000, description="URL изображения для проверки")
    
    @validator('url')
    def validate_url(cls, v):
        """Валидация URL"""
        if not re.match(r'^https?://', v, re.IGNORECASE):
            raise ValueError('URL должен начинаться с http:// или https://')
        
        # url_lower = v.lower()
        # if not (url_lower.endswith('.jpg') or url_lower.endswith('.jpeg')):
        #     raise ValueError('Поддерживаются только изображения формата JPG/JPEG')
        
        return v


class ImageValidationResponse(BaseModel):
    """Схема для ответа валидации изображения"""
    is_valid: bool = Field(..., description="Валидность изображения")
    message: str = Field(..., description="Сообщение о результате проверки")
    details: Optional[dict] = Field(None, description="Детали проверки")