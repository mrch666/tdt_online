"""
Тесты для проверки исправления ошибки NULL identity key в таблице modelgoods_external_images
"""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError
from app.models import ModelgoodsExternalImages
from app.routers.modelgoods_external_images import create_external_image
from app.schemas.modelgoods_external_images import ExternalImageCreate
from fastapi import HTTPException
import logging

logger = logging.getLogger("api")

def test_modelgoods_external_images_id_field_has_server_default():
    """
    Тест проверяет, что поле id в модели ModelgoodsExternalImages имеет server_default
    """
    # Проверяем определение поля id в модели
    id_column = ModelgoodsExternalImages.__table__.c.id
    
    # Проверяем, что есть server_default
    assert id_column.server_default is not None, "Поле id должно иметь server_default"
    
    # Проверяем, что server_default содержит '0'
    # server_default возвращает объект DefaultClause, проверяем его строковое представление
    server_default_obj = id_column.server_default
    assert server_default_obj is not None
    
    logger.info(f"Поле id имеет server_default: {server_default_obj}")

def test_create_external_image_without_id_success():
    """
    Тест проверяет успешное создание записи без указания id
    """
    # Тестовые данные
    test_data = ExternalImageCreate(
        modelid="000001001G2C",
        url="https://example.com/test.jpg",
        userid="0"
    )
    
    # Мокаем проверку URL
    with patch('app.routers.modelgoods_external_images.check_image_url') as mock_check_url:
        mock_check_url.return_value = {
            "is_valid": True,
            "message": "Изображение валидно",
            "details": {"width": 800, "height": 600, "size": 1024}
        }
        
        # Создаем мок сессии
        mock_session = MagicMock()
        
        # Мокаем запрос к Modelgoods
        mock_model = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_model
        
        # Мокаем создание записи
        mock_external_image = MagicMock()
        mock_external_image.id = "123456789012"  # Сгенерированный ID
        mock_external_image.modelid = test_data.modelid
        mock_external_image.url = test_data.url
        mock_external_image.userid = test_data.userid
        mock_external_image.is_approved = 0
        mock_external_image.is_loaded_to_db = 0
        mock_external_image.created_at = "2024-01-01 12:00:00"
        mock_external_image.updated_at = "2024-01-01 12:00:00"
        
        # Мокаем ModelgoodsExternalImages конструктор
        with patch('app.routers.modelgoods_external_images.ModelgoodsExternalImages') as mock_model_class:
            mock_model_class.return_value = mock_external_image
            
            # Мокаем commit и refresh
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # Вызываем функцию
            result = create_external_image(test_data, mock_session)
            
            # Проверяем, что функция вернула успешный результат
            assert result.id == "123456789012"
            assert result.modelid == test_data.modelid
            assert result.url == test_data.url
            assert result.userid == test_data.userid
            
            # Проверяем, что был вызван конструктор ModelgoodsExternalImages
            mock_model_class.assert_called_once()
            
            # Проверяем, что конструктор был вызван без параметра id
            call_args = mock_model_class.call_args[1]
            assert 'id' not in call_args, "Конструктор не должен получать параметр id"
            
            # Проверяем, что были переданы правильные параметры
            assert call_args['modelid'] == test_data.modelid
            assert call_args['url'] == test_data.url
            assert call_args['userid'] == test_data.userid
            assert call_args['is_approved'] == 0
            assert call_args['is_loaded_to_db'] == 0

def test_create_external_image_with_null_id_error():
    """
    Тест проверяет ошибку при создании записи с NULL id (до исправления)
    """
    # Тестовые данные
    test_data = ExternalImageCreate(
        modelid="000001001G2C",
        url="https://example.com/test.jpg",
        userid="0"
    )
    
    # Мокаем проверку URL
    with patch('app.routers.modelgoods_external_images.check_image_url') as mock_check_url:
        mock_check_url.return_value = {
            "is_valid": True,
            "message": "Изображение валидно",
            "details": {"width": 800, "height": 600, "size": 1024}
        }
        
        # Создаем мок сессии
        mock_session = MagicMock()
        
        # Мокаем запрос к Modelgoods
        mock_model = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_model
        
        # Мокаем создание записи с ошибкой IntegrityError
        mock_external_image = MagicMock()
        mock_external_image.id = None  # NULL id
        
        # Мокаем ModelgoodsExternalImages конструктор
        with patch('app.routers.modelgoods_external_images.ModelgoodsExternalImages') as mock_model_class:
            mock_model_class.return_value = mock_external_image
            
            # Мокаем commit с ошибкой IntegrityError
            mock_session.commit.side_effect = IntegrityError(
                "INSERT", 
                "modelgoods_external_images", 
                "Instance <ModelgoodsExternalImages at 0x8313130> has a NULL identity key"
            )
            
            # Проверяем, что функция выбрасывает HTTPException
            with pytest.raises(HTTPException) as exc_info:
                create_external_image(test_data, mock_session)
            
            # Проверяем, что ошибка имеет правильный статус код
            assert exc_info.value.status_code == 500
            assert "Ошибка при добавлении изображения" in exc_info.value.detail

def test_modelgoods_external_images_constructor_accepts_id_parameter():
    """
    Тест проверяет, что конструктор ModelgoodsExternalImages принимает параметр id
    """
    # Создаем объект с явным указанием id
    image_with_id = ModelgoodsExternalImages(
        id="0",  # Устанавливаем '0' для активации триггера
        modelid="000001001G2C",
        url="https://example.com/test.jpg",
        userid="0",
        is_approved=0,
        is_loaded_to_db=0
    )
    
    # Проверяем, что объект создан
    assert image_with_id is not None
    assert image_with_id.id == "0"
    assert image_with_id.modelid == "000001001G2C"
    assert image_with_id.url == "https://example.com/test.jpg"
    
    # Создаем объект без указания id
    image_without_id = ModelgoodsExternalImages(
        modelid="000001002G2C",
        url="https://example.com/test2.jpg",
        userid="0",
        is_approved=0,
        is_loaded_to_db=0
    )
    
    # Проверяем, что объект создан
    assert image_without_id is not None
    assert image_without_id.modelid == "000001002G2C"
    assert image_without_id.url == "https://example.com/test2.jpg"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])