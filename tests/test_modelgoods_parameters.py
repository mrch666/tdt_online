import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import get_db, engine
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv
import fdb

# Загружаем переменные окружения
load_dotenv()

# Устанавливаем путь к fbclient.dll
FBCLIENT_PATH = os.getenv('FBCLIENT_PATH', 'C:\\Program Files (x86)\\tdt3\\fbclient.dll')
os.environ['FBCLIENT'] = FBCLIENT_PATH

# Используем тестовую базу данных из .env
DATABASE_TEST_NAME = os.getenv('DATABASE_TEST_NAME', 'TDTBASE_TEST.FDB')
BASE_DIR = os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases')
TEST_DATABASE_URL = f"firebird+fdb://{os.getenv('FIREBIRD_USER')}:{os.getenv('FIREBIRD_PASSWORD')}@{os.getenv('FIREBIRD_HOST')}:{os.getenv('FIREBIRD_PORT')}/{BASE_DIR}\\{DATABASE_TEST_NAME}"

# Настройка тестовой базы данных
test_engine = create_engine(TEST_DATABASE_URL, connect_args={'fb_library_name': FBCLIENT_PATH})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Фикстуры
@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        # Проверяем подключение к тестовой базе
        result = db.execute(text("SELECT 1 FROM RDB$DATABASE")).fetchone()
        print(f"Подключение к тестовой базе успешно: {result}")
        
        # Очищаем тестовые данные перед тестом
        try:
            db.execute(text("DELETE FROM modelgoods WHERE id LIKE 'test%'"))
            db.commit()
        except:
            pass
        
        yield db
    finally:
        # Очищаем тестовые данные после теста
        try:
            db.execute(text("DELETE FROM modelgoods WHERE id LIKE 'test%'"))
            db.commit()
        except:
            pass
        db.close()

@pytest.fixture
def client(db):
    # Создаем функцию-генератор, как это делает оригинальный get_db
    def override_get_db():
        try:
            yield db
        finally:
            pass  # Не закрываем соединение, так как оно управляется фикстурой db
    
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
    # Используем modelid, для которого точно нет файла, но с правильной длиной (12 символов)
    response = client.get("/modelgoods/parameters/000000000000/weight")
    # Ожидаем 404, так как файла нет
    assert response.status_code == 404
    assert "Параметры не найдены" in response.text or "Параметр не найден" in response.text

def test_invalid_parameter_name(client):
    # Endpoint принимает любые имена параметров, поэтому ожидаем успешное создание
    response = client.post(
        "/modelgoods/parameters/test123/invalid_param",
        json={"value": "42"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_server_error_handling(client, mocker, db):
    # Мокаем хранимую процедуру
    mocker.patch("app.routers.modelgoods_parameters.text", 
                side_effect=Exception("Mocked error"))
    
    response = client.post(
        "/modelgoods/parameters/test123/weight",
        json={"value": "42"}
    )
    assert response.status_code == 500
    # Проверяем, что возвращается ошибка сервера (на русском или английском)
    assert "error" in response.text.lower() or "ошибка" in response.text.lower()
