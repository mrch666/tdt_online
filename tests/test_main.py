import pytest
import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

base_dir = os.getenv('BASE_DIR').replace('\\', '/')
SQLALCHEMY_DATABASE_URL = f"firebird+fdb://{os.getenv('FIREBIRD_USER')}:{os.getenv('FIREBIRD_PASSWORD')}@{os.getenv('FIREBIRD_HOST')}:{os.getenv('FIREBIRD_PORT')}/{base_dir}/{os.getenv('DATABASE_TEST_NAME')}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "fb_library_name": os.path.join(os.getenv('BASE_DIR'), "fbclient.dll")
    }
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_get_products_success(test_client):
    response = test_client.get("/products/")
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
