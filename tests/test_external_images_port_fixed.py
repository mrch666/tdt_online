"""
Тесты для проверки исправления проблемы с портом
"""
import pytest
import requests
import tempfile
import os
from unittest.mock import patch, MagicMock
from app.routers.web.pages import upload_to_main_api
from app.config import settings

def test_upload_to_main_api_uses_configuration():
    """
    Тест, который проверяет, что используется конфигурация для получения порта
    """
    # Создаем временный файл для теста
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        tmp_file.write(b'test image content')
        tmp_path = tmp_file.name
    
    try:
        # Мокаем requests.post для имитации успешного ответа
        with patch('requests.post') as mock_post:
            # Создаем мок ответа с успешным статусом
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success", "filename": "test.jpg"}
            mock_post.return_value = mock_response
            
            # Мокаем settings.get_modelgoods_image_url для возврата тестового URL
            with patch('app.routers.web.pages.settings.get_modelgoods_image_url') as mock_get_url:
                test_url = "http://localhost:8000/modelgoods/image/"
                mock_get_url.return_value = test_url
                
                # Вызываем функцию
                result = upload_to_main_api("000001001G2C", tmp_path)
                
                # Проверяем, что функция вернула успех
                assert result["status"] == "success"
                assert result["filename"] == "test.jpg"
                
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

def test_upload_to_main_api_success():
    """
    Тест успешной загрузки изображения через API
    """
    # Создаем временный файл для теста
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        tmp_file.write(b'test image content')
        tmp_path = tmp_file.name
    
    try:
        # Мокаем requests.post для имитации успешного ответа
        with patch('requests.post') as mock_post:
            # Создаем мок ответа с успешным статусом
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success", 
                "filename": "00000100_1G2C.jpg"
            }
            mock_post.return_value = mock_response
            
            # Вызываем функцию
            result = upload_to_main_api("000001001G2C", tmp_path)
            
            # Проверяем результат
            assert result["status"] == "success"
            assert result["filename"] == "00000100_1G2C.jpg"
            
            # Проверяем параметры вызова
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args[1]
            assert 'files' in call_kwargs
            assert 'data' in call_kwargs
            assert call_kwargs['data']['modelid'] == "000001001G2C"
            assert call_kwargs['timeout'] == 60
    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_upload_to_main_api_connection_error():
    """
    Тест ошибки соединения с API
    """
    # Создаем временный файл для теста
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        tmp_file.write(b'test image content')
        tmp_path = tmp_file.name
    
    try:
        # Мокаем requests.post для имитации ошибки соединения
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
            
            # Вызываем функцию
            result = upload_to_main_api("000001001G2C", tmp_path)
            
            # Проверяем, что функция вернула ошибку
            assert result["status"] == "error"
            assert "Connection refused" in result["message"]
    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_upload_to_main_api_timeout_error():
    """
    Тест ошибки таймаута при обращении к API
    """
    # Создаем временный файл для теста
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        tmp_file.write(b'test image content')
        tmp_path = tmp_file.name
    
    try:
        # Мокаем requests.post для имитации таймаута
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ReadTimeout("Read timed out")
            
            # Вызываем функцию
            result = upload_to_main_api("000001001G2C", tmp_path)
            
            # Проверяем, что функция вернула ошибку
            assert result["status"] == "error"
            assert "Read timed out" in result["message"]
    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])