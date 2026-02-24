"""
Тесты для воспроизведения ошибок с портом и API эндпоинтами
"""
import pytest
import requests
import tempfile
import os
from unittest.mock import patch, MagicMock
from app.routers.web.pages import upload_to_main_api, download_and_convert_image
from fastapi import HTTPException

def test_upload_to_main_api_uses_configuration_from_env():
    """
    Тест, который проверяет, что используется конфигурация из переменных окружения
    """
    # Создаем временный файл для теста
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        tmp_file.write(b'test image content')
        tmp_path = tmp_file.name
    
    try:
        # Мокаем requests.post для имитации ошибки таймаута
        with patch('requests.post') as mock_post:
            # Настраиваем мок для имитации таймаута
            mock_post.side_effect = requests.exceptions.ReadTimeout("Read timed out")
            
            # Мокаем settings.get_modelgoods_image_url для возврата тестового URL
            with patch('app.routers.web.pages.settings.get_modelgoods_image_url') as mock_get_url:
                test_url = "http://localhost:8000/modelgoods/image/"
                mock_get_url.return_value = test_url
                
                # Вызываем функцию, которая должна упасть с ошибкой
                result = upload_to_main_api("000001001G2C", tmp_path)
                
                # Проверяем, что функция вернула ошибку
                assert result["status"] == "error"
                assert "Read timed out" in result["message"]
                
                # Проверяем, что был вызов с URL из конфигурации
                mock_post.assert_called_once()
                call_args = mock_post.call_args[0][0]
                assert call_args == test_url
                
                # Проверяем, что был вызван метод получения URL из конфигурации
                mock_get_url.assert_called_once()
    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_upload_to_main_api_404_error_with_configuration():
    """
    Тест, который проверяет ошибку 404 при обращении к API с использованием конфигурации
    """
    # Создаем временный файл для теста
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        tmp_file.write(b'test image content')
        tmp_path = tmp_file.name
    
    try:
        # Мокаем requests.post для имитации 404 ошибки
        with patch('requests.post') as mock_post:
            # Создаем мок ответа с 404 статусом
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            mock_post.return_value = mock_response
            
            # Мокаем settings.get_modelgoods_image_url для возврата тестового URL
            with patch('app.routers.web.pages.settings.get_modelgoods_image_url') as mock_get_url:
                test_url = "http://localhost:8000/modelgoods/image/"
                mock_get_url.return_value = test_url
                
                # Вызываем функцию
                result = upload_to_main_api("000001001G2C", tmp_path)
                
                # Проверяем, что функция вернула ошибку
                assert result["status"] == "error"
                assert "API endpoint не найден" in result["message"]
                
                # Проверяем, что был вызов с URL из конфигурации
                mock_post.assert_called_once()
                call_args = mock_post.call_args[0][0]
                assert call_args == test_url
                
                # Проверяем, что был вызван метод получения URL из конфигурации
                mock_get_url.assert_called_once()
    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_download_and_convert_image_success():
    """
    Тест успешного скачивания и конвертации изображения
    """
    # Мокаем requests.get для имитации успешного скачивания
    with patch('requests.get') as mock_get:
        # Создаем мок ответа с тестовым изображением
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'test image content'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Мокаем PIL.Image.open
        with patch('PIL.Image.open') as mock_image_open:
            # Создаем мок изображения
            mock_image = MagicMock()
            mock_image.mode = 'RGB'
            mock_image.size = (100, 100)
            mock_image.save = MagicMock()
            mock_image_open.return_value = mock_image
            
            # Вызываем функцию
            temp_file = download_and_convert_image("https://example.com/test.jpg")
            
            # Проверяем, что функция вернула временный файл
            assert temp_file is not None
            assert os.path.exists(temp_file.name)
            
            # Очистка
            temp_file.close()
            os.unlink(temp_file.name)

def test_download_and_convert_image_failure():
    """
    Тест ошибки при скачивании изображения
    """
    # Мокаем requests.get для имитации ошибки
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Проверяем, что функция выбрасывает HTTPException
        with pytest.raises(HTTPException) as exc_info:
            download_and_convert_image("https://example.com/test.jpg")
        
        assert exc_info.value.status_code == 400
        assert "Ошибка при скачивании изображения" in exc_info.value.detail

def test_process_external_image_integration():
    """
    Интеграционный тест для проверки полного процесса обработки внешнего изображения
    """
    # Этот тест требует запущенного сервера, поэтому мы его пропустим в автоматических тестах
    pytest.skip("Требует запущенного сервера")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])