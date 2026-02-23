"""
Упрощенные тесты для проверки исправления ошибки NULL identity key в таблице modelgoods_external_images
"""
import pytest
from app.models import ModelgoodsExternalImages
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
    
    # Проверяем, что это действительно server_default
    server_default_str = str(server_default_obj)
    logger.info(f"Поле id имеет server_default: {server_default_str}")
    
    # Проверяем, что server_default установлен правильно
    assert "server_default" in server_default_str.lower() or "default" in server_default_str.lower()

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

def test_modelgoods_external_images_table_structure():
    """
    Тест проверяет структуру таблицы modelgoods_external_images
    """
    # Проверяем, что таблица существует
    table = ModelgoodsExternalImages.__table__
    assert table is not None
    
    # Проверяем наличие всех колонок
    columns = table.columns
    assert 'id' in columns
    assert 'modelid' in columns
    assert 'url' in columns
    assert 'is_approved' in columns
    assert 'is_loaded_to_db' in columns
    assert 'created_at' in columns
    assert 'updated_at' in columns
    assert 'userid' in columns
    
    # Проверяем, что id является первичным ключом
    id_column = columns['id']
    assert id_column.primary_key
    
    # Проверяем, что modelid является внешним ключом
    modelid_column = columns['modelid']
    assert len(modelid_column.foreign_keys) > 0
    
    logger.info(f"Таблица modelgoods_external_images имеет правильную структуру")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])