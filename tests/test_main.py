import os
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

@pytest.fixture(scope="module")
def test_image():
    # Создаем временный файл изображения
    with open("test_image.jpg", "wb") as f:
        f.write(b"fake_image_data")
    yield "test_image.jpg"
    os.remove("test_image.jpg")

def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_products():
    response = client.get("/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_upload_image(test_image):
    with open(test_image, "rb") as f:
        response = client.post(
            "/modelgoods/image/",
            files={"file": f},
            data={"modelid": "test123"}
        )
    assert response.status_code == 200
    assert "filename" in response.json()
