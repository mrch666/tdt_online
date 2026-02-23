"""
Тесты для веб-страницы управления внешними изображениями
"""
import sys
import os
sys.path.insert(0, '.')

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Modelgoods, ModelgoodsExternalImages
import tempfile
from unittest.mock import patch, MagicMock

# Тестовая база данных SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_external_images_web.db"

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

# Тестовые данные
TEST_PRODUCT_1 = {
    "id": "000001001G2C",
    "name": "Тестовый товар 1",
    "comment": "Описание товара 1"
}

TEST_PRODUCT_2 = {
    "id": "000001002Qa{",
    "name": "Тестовый товар 2",
    "comment": "Описание товара 2"
}

TEST_IMAGE_1 = {
    "id": "000000000001",
    "modelid": "000001001G2C",
    "url": "https://example.com/image1.jpg",
    "is_approved": 0,
    "is_loaded_to_db": 0,
    "userid": "0"
}

TEST_IMAGE_2 = {
    "id": "000000000002",
    "modelid": "000001001G2C",
    "url": "https://example.com/image2.jpg",
    "is_approved": 0,
    "is_loaded_to_db": 0,
    "userid": "0"
}

TEST_IMAGE_3 = {
    "id": "000000000003",
    "modelid": "000001002Qa{",
    "url": "https://example.com/image3.jpg",
    "is_approved": 1,
    "is_loaded_to_db": 1,  # Успешно загружено - товар должен скрываться
    "userid": "0"
}

TEST_IMAGE_4 = {
    "id": "000000000004",
    "modelid": "000001002Qa{",
    "url": "https://example.com/image4.jpg",
    "is_approved": 1,
    "is_loaded_to_db": 0,  # Подтверждено, но не загружено (ошибка)
    "userid": "0"
}

def setup_module(module):
    """Настройка тестовой базы данных"""
    db = TestingSessionLocal()
    
    # Очищаем таблицы
    db.query(ModelgoodsExternalImages).delete()
    db.query(Modelgoods).delete()
    db.commit()
    
    # Добавляем тестовые товары
    product1 = Modelgoods(**TEST_PRODUCT_1)
    product2 = Modelgoods(**TEST_PRODUCT_2)
    db.add(product1)
    db.add(product2)
    db.commit()
    
    # Добавляем тестовые изображения
    image1 = ModelgoodsExternalImages(**TEST_IMAGE_1)
    image2 = ModelgoodsExternalImages(**TEST_IMAGE_2)
    image3 = ModelgoodsExternalImages(**TEST_IMAGE_3)
    image4 = ModelgoodsExternalImages(**TEST_IMAGE_4)
    db.add(image1)
    db.add(image2)
    db.add(image3)
    db.add(image4)
    db.commit()
    
    db.close()

def teardown_module(module):
    """Очистка после тестов"""
    os.remove("test_external_images_web.db")

class TestExternalImagesWebPage:
    """Тесты веб-страницы управления внешними изображениями"""
    
    def test_web_page_exists(self):
        """Тест 1: Веб-страница должна существовать"""
        response = client.get("/web/external-images/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_web_page_shows_products(self):
        """Тест 2: Страница должна показывать товары с внешними изображениями"""
        response = client.get("/web/external-images/")
        html = response.text
        
        # Должны отображаться товары
        assert TEST_PRODUCT_1["name"] in html
        assert TEST_PRODUCT_1["id"] in html
        
        # Товар с успешно загруженным изображением должен скрываться
        assert TEST_PRODUCT_2["name"] not in html  # Должен быть скрыт
    
    def test_web_page_shows_images(self):
        """Тест 3: Страница должна показывать миниатюры изображений"""
        response = client.get("/web/external-images/")
        html = response.text
        
        # Должны быть миниатюры
        assert "thumbnail" in html
        assert "images-grid" in html
        
        # URL изображений должны быть в коде
        assert TEST_IMAGE_1["url"] in html
        assert TEST_IMAGE_2["url"] in html
    
    def test_web_page_shows_hidden_with_checkbox(self):
        """Тест 4: Скрытые товары должны показываться с параметром show_hidden"""
        response = client.get("/web/external-images/?show_hidden=true")
        html = response.text
        
        # Теперь оба товара должны отображаться
        assert TEST_PRODUCT_1["name"] in html
        assert TEST_PRODUCT_2["name"] in html
    
    def test_image_status_display(self):
        """Тест 5: Разные статусы изображений должны отображаться по-разному"""
        response = client.get("/web/external-images/?show_hidden=true")
        html = response.text
        
        # Изображение с is_approved=1, is_loaded_to_db=0 должно быть серым
        assert "image-gray" in html
        assert "grayscale" in html
        
        # Изображение с is_approved=0 должно быть кликабельным
        assert "image-clickable" in html
    
    def test_image_grid_layout(self):
        """Тест 6: Изображения должны располагаться в сетке 150x150px"""
        response = client.get("/web/external-images/")
        html = response.text
        
        # Проверяем CSS классы для сетки
        assert "grid-template-columns" in html or "display: grid" in html
        assert "150px" in html

class TestImageProcessingEndpoint:
    """Тесты endpoint'а для обработки изображений"""
    
    @patch('requests.get')
    @patch('requests.post')
    def test_process_image_success(self, mock_post, mock_get):
        """Тест 7: Успешная обработка изображения"""
        # Мок скачивания изображения
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'test image content'
        mock_get.return_value = mock_response
        
        # Мок загрузки в API
        mock_api_response = MagicMock()
        mock_api_response.status_code = 200
        mock_api_response.json.return_value = {"status": "success", "message": "Image uploaded"}
        mock_post.return_value = mock_api_response
        
        response = client.post(f"/web/external-images/{TEST_IMAGE_1['id']}/process")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "hide_product" in data
    
    @patch('requests.get')
    @patch('requests.post')
    def test_process_image_api_failure(self, mock_post, mock_get):
        """Тест 8: Ошибка при загрузке в API (изображение становится серым)"""
        # Мок скачивания изображения
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'test image content'
        mock_get.return_value = mock_response
        
        # Мок ошибки API
        mock_api_response = MagicMock()
        mock_api_response.status_code = 500
        mock_api_response.json.return_value = {"status": "error", "message": "API error"}
        mock_post.return_value = mock_api_response
        
        response = client.post(f"/web/external-images/{TEST_IMAGE_2['id']}/process")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert data["image_gray"] == True
    
    @patch('requests.get')
    def test_process_image_download_failure(self, mock_get):
        """Тест 9: Ошибка при скачивании изображения"""
        # Мок ошибки скачивания
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        response = client.post(f"/web/external-images/{TEST_IMAGE_1['id']}/process")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
    
    def test_process_already_approved_image(self):
        """Тест 10: Попытка обработки уже подтвержденного изображения"""
        # Пытаемся обработать изображение, которое уже is_approved=1
        response = client.post(f"/web/external-images/{TEST_IMAGE_4['id']}/process")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "уже подтверждено" in data["error"]

class TestImageConversion:
    """Тесты конвертации изображений в JPG"""
    
    @patch('requests.get')
    def test_webp_to_jpg_conversion(self, mock_get):
        """Тест 11: Конвертация WebP в JPG"""
        # Создаем тестовое WebP изображение
        from PIL import Image
        import io
        
        # Создаем простое изображение в памяти
        img = Image.new('RGB', (100, 100), color='red')
        
        # Сохраняем как WebP в буфер
        webp_buffer = io.BytesIO()
        img.save(webp_buffer, format='WEBP')
        webp_data = webp_buffer.getvalue()
        
        # Мок скачивания WebP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = webp_data
        mock_get.return_value = mock_response
        
        # Тестируем функцию конвертации
        from app.routers.web.pages import download_and_convert_image
        
        with patch('app.routers.web.pages.tempfile.NamedTemporaryFile') as mock_temp:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.jpg"
            mock_temp.return_value = mock_file
            
            # Мок для Image.open
            with patch('PIL.Image.open', return_value=img):
                # Мок для img.save
                img.save = MagicMock()
                
                result = download_and_convert_image("https://example.com/image.webp")
                
                # Проверяем, что сохраняется как JPG
                assert img.save.called
                call_args = img.save.call_args
                assert call_args[0][1] == 'JPEG'  # Второй аргумент - формат

class TestProductHidingLogic:
    """Тесты логики скрытия товаров"""
    
    def test_hide_product_with_loaded_image(self):
        """Тест 12: Товар скрывается если есть успешно загруженное изображение"""
        from app.routers.web.pages import get_products_with_external_images
        
        db = TestingSessionLocal()
        
        try:
            # Получаем товары без показа скрытых
            products = get_products_with_external_images(db, show_hidden=False)
            
            # Проверяем, что товар 2 скрыт (у него есть успешно загруженное изображение)
            product_ids = [p['product'].id for p in products]
            assert TEST_PRODUCT_2["id"] not in product_ids
            assert TEST_PRODUCT_1["id"] in product_ids
            
            # Получаем товары с показом скрытых
            products_all = get_products_with_external_images(db, show_hidden=True)
            product_ids_all = [p['product'].id for p in products_all]
            
            # Теперь оба товара должны быть
            assert TEST_PRODUCT_1["id"] in product_ids_all
            assert TEST_PRODUCT_2["id"] in product_ids_all
            
        finally:
            db.close()

if __name__ == "__main__":
    # Запуск тестов
    setup_module(None)
    
    try:
        # Создаем экземпляр тестового класса
        test_class = TestExternalImagesWebPage()
        
        # Запускаем тесты по порядку
        print("Запуск тестов веб-страницы управления внешними изображениями...")
        
        test_class.test_web_page_exists()
        print("✓ Тест 1: Веб-страница существует")
        
        test_class.test_web_page_shows_products()
        print("✓ Тест 2: Страница показывает товары")
        
        test_class.test_web_page_shows_images()
        print("✓ Тест 3: Страница показывает миниатюры")
        
        test_class.test_web_page_shows_hidden_with_checkbox()
        print("✓ Тест 4: Скрытые товары показываются с чекбоксом")
        
        test_class.test_image_status_display()
        print("✓ Тест 5: Статусы изображений отображаются правильно")
        
        test_class.test_image_grid_layout()
        print("✓ Тест 6: Изображения в сетке 150x150px")
        
        print("\nВсе тесты веб-страницы пройдены успешно!")
        
    except AssertionError as e:
        print(f"✗ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
    finally:
        teardown_module(None)