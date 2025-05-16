import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import get_db
import xml.etree.ElementTree as ET

# Настройка тестовой базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Фикстуры
@pytest.fixture(scope="module")
def db():
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS modelgoods (
                id TEXT PRIMARY KEY,
                changedate TIMESTAMP
            )""")
        )
        # Mock хранимой процедуры
        # Create table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS wp_SaveBlobToFile (
                file_path TEXT PRIMARY KEY,
                content BLOB,
                result INTEGER
            )"""))
        db.commit()
        
        # Insert test data
        db.execute(text("""
            INSERT OR IGNORE INTO wp_SaveBlobToFile (file_path, content, result)
            VALUES ('dummy_path', CAST('dummy_content' AS BLOB), 1)"""))
        db.commit()
        yield db
    finally:
        db.execute(text("DROP TABLE IF EXISTS modelgoods"))
        db.execute(text("DROP TABLE IF EXISTS wp_SaveBlobToFile"))
        db.commit()
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# Тестовые случаи
def test_create_and_get_parameter(client):
    # Тест создания параметра
    response = client.post(
        "/modelgoods/parameters/test123/weight",
        json={"value": "42"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Тест получения параметра
    response = client.get("/modelgoods/parameters/test123/weight")
    assert response.status_code == 200
    assert response.json() == {"value": "42"}

def test_update_parameter(client):
    # Создаем параметр
    client.post("/modelgoods/parameters/test123/weight", json={"value": "42"})
    
    # Обновляем параметр
    response = client.post(
        "/modelgoods/parameters/test123/weight",
        json={"value": "45"}
    )
    assert response.status_code == 200

    # Проверяем обновление
    response = client.get("/modelgoods/parameters/test123/weight")
    assert response.json() == {"value": "45"}

def test_get_full_xml(client):
    # Создаем несколько параметров
    client.post("/modelgoods/parameters/test123/weight", json={"value": "42"})
    client.post("/modelgoods/parameters/test123/height", json={"value": "150"})

    # Получаем полный XML
    response = client.get("/modelgoods/parameters/test123")
    assert response.status_code == 200
    
    # Парсим XML
    root = ET.fromstring(response.content)
    assert root.find("weight").text == "42"
    assert root.find("height").text == "150"

def test_parameter_not_found(client):
    response = client.get("/modelgoods/parameters/test123/weight")
    assert response.status_code in (404, 422)  # 422 для ошибки валидации FastAPI
    assert "Параметр не найден" in response.text

def test_invalid_parameter_name(client):
    response = client.post(
        "/modelgoods/parameters/test123/invalid_param",
        json={"value": "42"}
    )
    assert response.status_code == 404

def test_server_error_handling(client, mocker, db):
    # Мокаем хранимую процедуру
    mocker.patch("app.routers.modelgoods_parameters.text", 
                side_effect=Exception("Mocked error"))
    
    response = client.post(
        "/modelgoods/parameters/test123/weight",
        json={"value": "42"}
    )
    assert response.status_code == 500
    assert "Internal server error" in response.text
