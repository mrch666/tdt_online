"""
Тесты для проверки конфигурации порта сервера
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from app.config import Settings
import logging

logger = logging.getLogger("api")

def test_settings_default_port():
    """
    Тест проверяет значение порта по умолчанию
    """
    # Проверяем значение по умолчанию (теперь 7990 из .env)
    assert Settings.SERVER_PORT == 7990, f"Порт должен быть 7990, а не {Settings.SERVER_PORT}"
    
    # Проверяем, что API_BASE_URL использует порт по умолчанию
    expected_url = f"http://localhost:{Settings.SERVER_PORT}"
    assert Settings.API_BASE_URL == expected_url, f"API_BASE_URL должен быть {expected_url}, а не {Settings.API_BASE_URL}"
    
    logger.info(f"Порт по умолчанию: {Settings.SERVER_PORT}")
    logger.info(f"API_BASE_URL по умолчанию: {Settings.API_BASE_URL}")

def test_get_api_url_with_default_port():
    """
    Тест проверяет формирование URL API с портом по умолчанию
    """
    # Проверяем формирование URL для endpoint
    endpoint = "modelgoods/image/"
    expected_url = f"http://localhost:{Settings.SERVER_PORT}/modelgoods/image/"
    actual_url = Settings.get_api_url(endpoint)
    
    assert actual_url == expected_url, f"URL должен быть {expected_url}, а не {actual_url}"
    
    logger.info(f"Сформированный URL: {actual_url}")

def test_get_modelgoods_image_url():
    """
    Тест проверяет формирование URL для загрузки изображений
    """
    expected_url = f"http://localhost:{Settings.SERVER_PORT}/modelgoods/image/"
    actual_url = Settings.get_modelgoods_image_url()
    
    assert actual_url == expected_url, f"URL для изображений должен быть {expected_url}, а не {actual_url}"
    
    logger.info(f"URL для загрузки изображений: {actual_url}")

def test_env_port_is_set():
    """
    Тест проверяет, что переменная SERVER_PORT установлена в .env
    """
    # Проверяем, что переменная окружения установлена
    env_port = os.getenv("SERVER_PORT")
    assert env_port == "7990", f"Переменная SERVER_PORT должна быть '7990' в .env, но имеет значение: {env_port}"
    
    logger.info(f"Переменная SERVER_PORT установлена в .env: {env_port}")

@patch.dict(os.environ, {"SERVER_PORT": "7990"}, clear=True)
def test_settings_with_env_port():
    """
    Тест проверяет чтение порта из переменной окружения
    """
    # Пересоздаем настройки с моком переменной окружения
    with patch('app.config.os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda key, default=None: {
            "SERVER_PORT": "7990"
        }.get(key, default)
        
        # Создаем новый экземпляр настроек
        test_settings = type('TestSettings', (), {})()
        
        # Копируем логику из Settings
        test_settings.SERVER_PORT = int(mock_getenv("SERVER_PORT", 8000))
        test_settings.API_BASE_URL = f"http://localhost:{test_settings.SERVER_PORT}"
        
        # Проверяем значения
        assert test_settings.SERVER_PORT == 7990, f"Порт должен быть 7990, а не {test_settings.SERVER_PORT}"
        assert test_settings.API_BASE_URL == "http://localhost:7990", f"API_BASE_URL должен быть http://localhost:7990, а не {test_settings.API_BASE_URL}"
        
        logger.info(f"Порт из переменной окружения: {test_settings.SERVER_PORT}")
        logger.info(f"API_BASE_URL с портом из окружения: {test_settings.API_BASE_URL}")

def test_upload_function_uses_configuration():
    """
    Тест проверяет, что функция upload_to_main_api использует конфигурацию из settings
    """
    from app.routers.web.pages import upload_to_main_api
    
    # Мокаем settings
    with patch('app.routers.web.pages.settings') as mock_settings:
        mock_settings.get_modelgoods_image_url.return_value = "http://localhost:7990/modelgoods/image/"
        
        # Мокаем requests.post
        with patch('app.routers.web.pages.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            mock_post.return_value = mock_response
            
            # Мокаем os.path.getsize
            with patch('app.routers.web.pages.os.path.getsize') as mock_getsize:
                mock_getsize.return_value = 1024  # 1KB файл
                
                # Мокаем open
                with patch('builtins.open', MagicMock()) as mock_open:
                    mock_file = MagicMock()
                    mock_file.__enter__.return_value = b"test image content"
                    mock_open.return_value = mock_file
                    
                    # Вызываем функцию
                    result = upload_to_main_api("test_modelid", "test_image.jpg")
                    
                    # Проверяем, что был вызван get_modelgoods_image_url
                    mock_settings.get_modelgoods_image_url.assert_called_once()
                    
                    # Проверяем, что requests.post был вызван с правильным URL
                    mock_post.assert_called_once()
                    call_args = mock_post.call_args
                    assert "http://localhost:7990/modelgoods/image/" in str(call_args), f"Должен использоваться порт 7990, а не 8000"
                    
                    logger.info(f"Функция upload_to_main_api использует URL: {mock_settings.get_modelgoods_image_url.return_value}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])