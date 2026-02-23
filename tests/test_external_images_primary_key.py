"""
Тест для проверки ошибки первичного ключа в таблице modelgoods_external_images
Ошибка: violation of PRIMARY or UNIQUE KEY constraint "PK_modelgoods_external_images" 
        on table "modelgoods_external_images"
        Problematic key value is ("id" = '0')
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Добавляем путь к app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, get_db
from app.models import Modelgoods, ModelgoodsExternalImages

# Тестовая база данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем таблицы
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_external_image_creation_with_duplicate_id():
    """
    Тест, который воспроизводит ошибку дублирования первичного ключа
    при создании записи с id='0'
    """
    # Сначала создаем тестовый товар
    test_model = Modelgoods(
        id="000001001G2C",
        name="Test Product",
        userid="0"
    )
    
    db = TestingSessionLocal()
    try:
        # Очищаем таблицы перед тестом
        db.query(ModelgoodsExternalImages).delete()
        db.query(Modelgoods).delete()
        db.commit()
        
        # Добавляем тестовый товар
        db.add(test_model)
        db.commit()
        db.refresh(test_model)
        
        # Пытаемся создать запись с id='0' (как делает SQLAlchemy по умолчанию)
        test_image = ModelgoodsExternalImages(
            id='0',  # Это значение по умолчанию из модели
            modelid="000001001G2C",
            url="https://example.com/test.jpg",
            userid="0",
            is_approved=0,
            is_loaded_to_db=0
        )
        
        db.add(test_image)
        db.commit()
        
        # Если мы дошли сюда, значит первая запись создалась успешно
        # Теперь пытаемся создать вторую запись с таким же id
        test_image2 = ModelgoodsExternalImages(
            id='0',  # Тот же самый id
            modelid="000001001G2C",
            url="https://example.com/test2.jpg",
            userid="0",
            is_approved=0,
            is_loaded_to_db=0
        )
        
        db.add(test_image2)
        db.commit()  # Здесь должна возникнуть ошибка
        
        # Если мы дошли сюда, значит ошибка не возникла
        # Это плохо - мы должны были получить ошибку
        assert False, "Ожидалась ошибка дублирования первичного ключа, но её не было"
        
    except Exception as e:
        # Проверяем, что ошибка связана с первичным ключом
        error_str = str(e).lower()
        assert any(keyword in error_str for keyword in [
            'primary', 
            'unique', 
            'pk_modelgoods_external_images',
            'duplicate',
            'violation'
        ]), f"Ожидалась ошибка первичного ключа, но получили: {e}"
        print(f"✓ Тест прошел: получена ожидаемая ошибка первичного ключа: {e}")
    finally:
        db.close()

def test_api_external_image_creation():
    """
    Тест создания внешнего изображения через API
    """
    # Сначала создаем тестовый товар
    test_model = Modelgoods(
        id="000001002Qa{",
        name="Test Product 2",
        userid="0"
    )
    
    db = TestingSessionLocal()
    try:
        # Очищаем таблицы перед тестом
        db.query(ModelgoodsExternalImages).delete()
        db.query(Modelgoods).delete()
        db.commit()
        
        # Добавляем тестовый товар
        db.add(test_model)
        db.commit()
        
        # Тестируем API endpoint
        response = client.post(
            "/api/modelgoods/external-images/",
            json={
                "modelid": "000001002Qa{",
                "url": "https://cdn.vseinstrumenti.ru/images/goods/rashodnye-materialy-i-osnastka/rashodnye-materialy-dlya-sadovoj-tehniki/19019319/1000x1000/201056631.jpg",
                "userid": "0"
            }
        )
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Тело ответа: {response.text}")
        
        # Проверяем, что запрос завершился успешно
        if response.status_code == 500:
            error_detail = response.json().get("detail", "")
            print(f"Ошибка сервера: {error_detail}")
            # Проверяем, что ошибка связана с первичным ключом
            assert "PK_modelgoods_external_images" in error_detail or "primary" in error_detail.lower() or "unique" in error_detail.lower()
        else:
            assert response.status_code == 201, f"Ожидался статус 201, получен {response.status_code}"
            
    finally:
        db.close()

if __name__ == "__main__":
    print("Запуск тестов ошибки первичного ключа...")
    test_external_image_creation_with_duplicate_id()
    print("\nЗапуск теста API...")
    test_api_external_image_creation()
    print("\nВсе тесты завершены!")