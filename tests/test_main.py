import pytest
import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
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

def test_get_products_success(client):
    """Тест доступности роута /api/products/ для внешних приложений"""
    response = client.get("/api/products/")
    assert response.status_code == 200
    products = response.json()
    
    # Validate response structure
    assert isinstance(products, list)
    if products:  # Only validate if we got results
        product = products[0]
        assert "modelid" in product
        assert "name" in product
        assert "price" in product
        assert isinstance(product["price"], float)
        assert "barcode" in product
        assert "kmin" in product
        assert isinstance(product["kmin"], int)


# def test_get_products_error_handling(test_client):
#     # Force database error
#     original_get_db = app.dependency_overrides[get_db]
    
#     def faulty_get_db():
#         raise Exception("Database connection failed")
        
#     app.dependency_overrides[get_db] = faulty_get_db
    
#     response = test_client.get("/products/")
#     assert response.status_code == 500
#     assert "detail" in response.json()
    
#     app.dependency_overrides[get_db] = original_get_db  # Restore original

# def test_healthcheck(test_client):
#     response = test_client.get("/healthcheck")
#     assert response.status_code == 200
#     assert response.json() == {
#         "status": "ok",
#         "db_connection": "success"
#     }

# def test_healthcheck_db_failure(test_client):
#     # Force database failure
#     original_engine = engine
#     engine.dispose()  # Close connections
    
#     response = test_client.get("/healthcheck")
#     assert response.status_code == 500
#     assert "db_connection" in response.json()
#     assert response.json()["db_connection"] == "failed"
    
#     engine.connect()  # Restore connection
