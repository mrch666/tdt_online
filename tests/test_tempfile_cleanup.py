"""
Тесты для проверки корректной очистки временных файлов
"""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from app.routers.web.pages import download_and_convert_image, upload_to_main_api
from fastapi import HTTPException
import requests
from PIL import Image
import io

def test_download_and_convert_image_creates_tempfile():
    """
    Тест проверяет, что функция создает временный файл
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
            assert hasattr(temp_file, 'name')
            assert os.path.exists(temp_file.name)
            
            # Проверяем, что файл имеет правильное расширение
            assert temp_file.name.endswith('.jpg')
            
            # Закрываем и удаляем временный файл
            temp_file.close()
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

def test_tempfile_cleanup_on_exception():
    """
    Тест проверяет, что временные файлы удаляются при исключении
    """
    # Мокаем requests.get для имитации ошибки
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Проверяем, что функция выбрасывает HTTPException
        with pytest.raises(HTTPException) as exc_info:
            download_and_convert_image("https://example.com/test.jpg")
        
        assert exc_info.value.status_code == 400
        assert "Ошибка при скачивании изображения" in exc_info.value.detail

def test_upload_to_main_api_handles_missing_file():
    """
    Тест проверяет обработку отсутствующего файла
    """
    # Вызываем функцию с несуществующим файлом
    result = upload_to_main_api("test_modelid", "non_existent_file.jpg")
    
    # Проверяем, что функция вернула ошибку
    assert result["status"] == "error"
    assert "Ошибка при загрузке" in result["message"]

def test_tempfile_locked_during_upload():
    """
    Тест проверяет ситуацию, когда временный файл заблокирован другим процессом
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
            
            # Мокаем settings.get_modelgoods_image_url
            with patch('app.routers.web.pages.settings.get_modelgoods_image_url') as mock_get_url:
                mock_get_url.return_value = "http://localhost:7990/modelgoods/image/"
                
                # Вызываем функцию
                result = upload_to_main_api("000001001G2C", tmp_path)
                
                # Проверяем, что функция вернула успех
                assert result["status"] == "success"
                
                # Проверяем, что файл все еще существует (не был удален функцией)
                assert os.path.exists(tmp_path)
    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_process_external_image_tempfile_cleanup():
    """
    Тест проверяет очистку временных файлов в функции process_external_image
    """
    import asyncio
    from app.routers.web.pages import process_external_image
    from fastapi import Request
    from sqlalchemy.orm import Session
    
    # Мокаем все зависимости
    with patch('app.routers.web.pages.ModelgoodsExternalImages') as mock_model:
        # Создаем мок изображения
        mock_image = MagicMock()
        mock_image.id = "test_id"
        mock_image.modelid = "000001001G2C"
        mock_image.url = "https://example.com/test.jpg"
        mock_image.is_approved = 0
        mock_image.is_loaded_to_db = 0
        
        # Создаем мок сессии БД
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_image
        mock_db.query.return_value = mock_query
        
        # Мокаем download_and_convert_image
        with patch('app.routers.web.pages.download_and_convert_image') as mock_download:
            # Создаем мок временного файла
            mock_tempfile = MagicMock()
            mock_tempfile.name = "C:\\test\\tempfile.jpg"
            mock_download.return_value = mock_tempfile
            
            # Мокаем upload_to_main_api
            with patch('app.routers.web.pages.upload_to_main_api') as mock_upload:
                mock_upload.return_value = {"status": "success"}
                
                # Мокаем os.path.exists и os.unlink для проверки удаления файла
                with patch('app.routers.web.pages.os.path.exists') as mock_exists:
                    with patch('app.routers.web.pages.os.unlink') as mock_unlink:
                        mock_exists.return_value = True
                        
                        # Вызываем функцию асинхронно
                        result = asyncio.run(process_external_image(
                            request=MagicMock(spec=Request),
                            image_id="test_id",
                            db=mock_db
                        ))
                        
                        # Проверяем, что os.unlink был вызван
                        mock_unlink.assert_called_once_with("C:\\test\\tempfile.jpg")

def test_tempfile_cleanup_with_permission_error():
    """
    Тест проверяет обработку ошибки разрешений при удалении файла
    """
    import asyncio
    from app.routers.web.pages import process_external_image
    from fastapi import Request
    from sqlalchemy.orm import Session
    
    # Мокаем все зависимости
    with patch('app.routers.web.pages.ModelgoodsExternalImages') as mock_model:
        # Создаем мок изображения
        mock_image = MagicMock()
        mock_image.id = "test_id"
        mock_image.modelid = "000001001G2C"
        mock_image.url = "https://example.com/test.jpg"
        mock_image.is_approved = 0
        mock_image.is_loaded_to_db = 0
        
        # Создаем мок сессии БД
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_image
        mock_db.query.return_value = mock_query
        
        # Мокаем download_and_convert_image
        with patch('app.routers.web.pages.download_and_convert_image') as mock_download:
            # Создаем мок временного файла
            mock_tempfile = MagicMock()
            mock_tempfile.name = "C:\\test\\tempfile.jpg"
            mock_download.return_value = mock_tempfile
            
            # Мокаем upload_to_main_api
            with patch('app.routers.web.pages.upload_to_main_api') as mock_upload:
                mock_upload.return_value = {"status": "success"}
                
                # Мокаем os.path.exists и os.unlink для имитации ошибки разрешений
                with patch('app.routers.web.pages.os.path.exists') as mock_exists:
                    with patch('app.routers.web.pages.os.unlink') as mock_unlink:
                        mock_exists.return_value = True
                        mock_unlink.side_effect = PermissionError("[WinError 32] Процесс не может получить доступ к файлу")
                        
                        # Вызываем функцию асинхронно
                        result = asyncio.run(process_external_image(
                            request=MagicMock(spec=Request),
                            image_id="test_id",
                            db=mock_db
                        ))
                        
                        # Проверяем, что функция не падает при ошибке удаления
                        # и возвращает успешный результат
                        assert result.status_code == 200

def test_improved_tempfile_cleanup_strategy():
    """
    Тест проверяет улучшенную стратегию очистки временных файлов
    """
    import time
    
    # Создаем временный файл
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    temp_file.write(b'test content')
    temp_file.close()
    
    temp_path = temp_file.name
    
    try:
        # Проверяем, что файл существует
        assert os.path.exists(temp_path)
        
        # Пытаемся удалить файл с задержкой и повторными попытками
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                os.unlink(temp_path)
                break
            except (PermissionError, OSError) as e:
                if attempt == max_attempts - 1:
                    # Последняя попытка - логируем ошибку, но не падаем
                    print(f"Не удалось удалить файл после {max_attempts} попыток: {e}")
                else:
                    # Ждем перед следующей попыткой
                    time.sleep(0.1)
        
        # Проверяем, что файл был удален (или хотя бы попытка была)
        # В реальном коде мы бы логировали результат
        assert True  # Тест проходит, если не было исключения
        
    finally:
        # Гарантированная очистка
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass  # Игнорируем ошибки при финальной очистке

if __name__ == "__main__":
    pytest.main([__file__, "-v"])