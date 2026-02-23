"""
Тест для проверки исправления ошибки первичного ключа в таблице modelgoods_external_images
После исправления модели (удаление server_default=text("'0'") из поля id)
триггер должен корректно генерировать новый ID через функцию GetID
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Добавляем путь к app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, get_db
from app.models import Modelgoods, ModelgoodsExternalImages

# Тестовая база данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_fixed.db"

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

def test_model_without_server_default():
    """
    Тест проверяет, что модель ModelgoodsExternalImages не имеет server_default для поля id
    """
    # Проверяем определение поля id в модели
    id_column = ModelgoodsExternalImages.__table__.c.id
    
    print(f"Поле id имеет server_default: {id_column.server_default}")
    print(f"Поле id имеет default: {id_column.default}")
    
    # После исправления server_default должен быть None
    assert id_column.server_default is None, "Поле id не должно иметь server_default"
    
    print("OK Модель исправлена: поле id не имеет server_default")

def test_external_image_creation_without_id():
    """
    Тест создания записи без указания id (должен сгенерироваться автоматически)
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
        
        # Создаем запись без указания id
        test_image = ModelgoodsExternalImages(
            # id не указываем - должно сгенерироваться автоматически
            modelid="000001001G2C",
            url="https://example.com/test.jpg",
            userid="0",
            is_approved=0,
            is_loaded_to_db=0
        )
        
        db.add(test_image)
        db.commit()
        db.refresh(test_image)
        
        # Проверяем, что id был сгенерирован
        print(f"Сгенерированный ID: {test_image.id}")
        assert test_image.id is not None, "ID должен быть сгенерирован"
        assert test_image.id != '0', "ID не должен быть '0'"
        assert test_image.id != '', "ID не должен быть пустым"
        
        print(f"✓ Запись создана с ID: {test_image.id}")
        
        # Пытаемся создать вторую запись
        test_image2 = ModelgoodsExternalImages(
            modelid="000001001G2C",
            url="https://example.com/test2.jpg",
            userid="0",
            is_approved=0,
            is_loaded_to_db=0
        )
        
        db.add(test_image2)
        db.commit()
        db.refresh(test_image2)
        
        # Проверяем, что второй ID тоже сгенерирован и отличается от первого
        print(f"Второй сгенерированный ID: {test_image2.id}")
        assert test_image2.id is not None, "Второй ID должен быть сгенерирован"
        assert test_image2.id != test_image.id, "ID должны быть разными"
        
        print(f"✓ Вторая запись создана с ID: {test_image2.id}")
        print(f"✓ Ошибки дублирования первичного ключа нет!")
        
    except Exception as e:
        print(f"✗ Ошибка при создании записи: {e}")
        raise
    finally:
        db.close()

def test_api_external_image_creation_fixed():
    """
    Тест создания внешнего изображения через API после исправления
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
        
        if response.status_code == 201:
            data = response.json()
            print(f"Успешный ответ: {data}")
            assert 'id' in data, "Ответ должен содержать поле id"
            assert data['id'] is not None, "ID должен быть сгенерирован"
            assert data['id'] != '0', "ID не должен быть '0'"
            print(f"✓ API успешно создал запись с ID: {data['id']}")
        else:
            print(f"Тело ответа: {response.text}")
            # Даже если есть ошибка, она не должна быть связана с первичным ключом
            error_detail = response.json().get("detail", "")
            assert "PK_modelgoods_external_images" not in error_detail, "Ошибка не должна быть связана с первичным ключом"
            assert "primary" not in error_detail.lower(), "Ошибка не должна быть связана с первичным ключом"
            assert "unique" not in error_detail.lower(), "Ошибка не должна быть связана с уникальным ключом"
            
    finally:
        db.close()

def test_multiple_image_creation():
    """
    Тест создания нескольких изображений для одного товара
    """
    test_model = Modelgoods(
        id="TESTMODEL123",
        name="Test Model for Multiple Images",
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
        
        # Создаем 3 изображения
        image_ids = []
        for i in range(3):
            image = ModelgoodsExternalImages(
                modelid="TESTMODEL123",
                url=f"https://example.com/image{i}.jpg",
                userid="0",
                is_approved=0,
                is_loaded_to_db=0
            )
            
            db.add(image)
            db.commit()
            db.refresh(image)
            
            print(f"Изображение {i+1} создано с ID: {image.id}")
            assert image.id is not None, f"ID изображения {i+1} должен быть сгенерирован"
            assert image.id not in image_ids, f"ID изображения {i+1} должен быть уникальным"
            
            image_ids.append(image.id)
        
        print(f"✓ Создано {len(image_ids)} изображений с уникальными ID: {image_ids}")
        
        # Проверяем, что все ID разные
        assert len(set(image_ids)) == len(image_ids), "Все ID должны быть уникальными"
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Запуск тестов исправления ошибки первичного ключа...")
    
    try:
        test_model_without_server_default()
        print("\n" + "="*50 + "\n")
        
        test_external_image_creation_without_id()
        print("\n" + "="*50 + "\n")
        
        test_multiple_image_creation()
        print("\n" + "="*50 + "\n")
        
        test_api_external_image_creation_fixed()
        
        print("\n" + "="*50)
        print("Все тесты пройдены успешно! Ошибка первичного ключа исправлена.")
        print("="*50)
        
    except Exception as e:
        print(f"\n✗ Тесты не пройдены: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)