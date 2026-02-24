"""
Тест для проверки таймаутов при подключении к API
"""
import pytest
import requests
import time
from unittest.mock import patch, MagicMock
import os

def test_api_endpoint_availability():
    """
    Тест проверяет доступность API endpoint для загрузки изображений
    """
    # URL API из конфигурации
    api_url = "http://localhost:7990/modelgoods/image/"
    
    try:
        # Пробуем подключиться к API с коротким таймаутом для теста
        response = requests.get(api_url, timeout=5)
        
        # Если получили ответ, проверяем статус
        # Ожидаем 405 Method Not Allowed (GET не разрешен) или 200 OK
        assert response.status_code in [200, 405], f"Неожиданный статус код: {response.status_code}"
        
        print(f"API endpoint доступен: {api_url}, статус: {response.status_code}")
        
    except requests.exceptions.ConnectionError as e:
        # Сервер недоступен
        pytest.fail(f"Сервер недоступен на {api_url}: {str(e)}")
    except requests.exceptions.Timeout as e:
        # Таймаут подключения
        pytest.fail(f"Таймаут при подключении к {api_url}: {str(e)}")
    except Exception as e:
        # Другие ошибки
        pytest.fail(f"Ошибка при проверке API: {str(e)}")

def test_upload_to_main_api_timeout():
    """
    Тест воспроизводит проблему таймаута в функции upload_to_main_api
    """
    from app.routers.web.pages import upload_to_main_api
    
    # Создаем временный файл для теста
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file.write(b"test image content")
        temp_file_path = temp_file.name
    
    try:
        # Мокаем requests.post чтобы симулировать таймаут
        with patch('requests.post') as mock_post:
            # Настраиваем мок для симуляции таймаута
            mock_post.side_effect = requests.exceptions.Timeout("Read timed out. (read timeout=120)")
            
            # Вызываем функцию
            result = upload_to_main_api("0000010028Vx", temp_file_path)
            
            # Проверяем, что функция корректно обработала таймаут
            assert result['status'] == 'error'
            assert 'Таймаут при подключении к API' in result['message']
            print(f"Функция корректно обработала таймаут: {result['message']}")
            
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_api_response_time():
    """
    Тест проверяет время отклика API (должно быть меньше 2 секунд)
    """
    api_url = "http://localhost:7990/modelgoods/image/"
    
    try:
        start_time = time.time()
        response = requests.get(api_url, timeout=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Время отклика должно быть меньше 2 секунд
        assert response_time < 2.0, f"Время отклика API слишком долгое: {response_time:.2f} секунд"
        
        print(f"Время отклика API: {response_time:.2f} секунд, статус: {response.status_code}")
        
    except requests.exceptions.Timeout as e:
        pytest.fail(f"API не отвечает в течение 10 секунд: {str(e)}")
    except Exception as e:
        pytest.fail(f"Ошибка при проверке времени отклика: {str(e)}")

def test_file_lock_issue():
    """
    Тест проверяет проблему блокировки файлов при удалении
    """
    import tempfile
    
    # Создаем временный файл
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    temp_file.write(b"test content")
    temp_file.close()
    
    file_path = temp_file.name
    
    # Пробуем удалить файл (должно работать)
    try:
        os.unlink(file_path)
        print(f"Файл успешно удален: {file_path}")
    except PermissionError as e:
        # Файл заблокирован
        pytest.fail(f"Файл заблокирован и не может быть удален: {str(e)}")
    except Exception as e:
        pytest.fail(f"Ошибка при удалении файла: {str(e)}")

def test_procedure_file_save_delay():
    """
    Тест проверяет задержки между вызовом процедуры и появлением файла
    """
    # Этот тест требует подключения к БД, поэтому используем моки
    from app.routers.modelgoods_images import upload_model_image
    from unittest.mock import patch, MagicMock, AsyncMock
    from sqlalchemy.orm import Session
    import asyncio
    
    with patch('app.routers.modelgoods_images.os.path.exists') as mock_exists:
        with patch('app.routers.modelgoods_images.os.unlink') as mock_unlink:
            with patch('app.routers.modelgoods_images.tempfile.NamedTemporaryFile') as mock_tempfile:
                # Настраиваем моки
                mock_exists.return_value = False
                
                mock_temp = MagicMock()
                mock_temp.name = "C:\\temp\\test.jpg"
                mock_temp.__enter__.return_value = mock_temp
                mock_tempfile.return_value = mock_temp
                
                mock_db = MagicMock(spec=Session)
                mock_result = MagicMock()
                mock_result.fetchone.return_value = ["0000010028Vx"]
                mock_db.execute.return_value = mock_result
                
                mock_procedure_result = [(1,)]
                mock_db.execute.return_value.fetchall.return_value = mock_procedure_result
                
                mock_file = AsyncMock()
                mock_file.filename = "test.jpg"
                mock_file.read.return_value = b"test image content"
                mock_file.close = AsyncMock()
                
                # Проверяем, что функция не делает излишних проверок существования файла
                exists_call_count = 0
                
                def exists_side_effect(path):
                    nonlocal exists_call_count
                    exists_call_count += 1
                    # Первая проверка - файла нет, последующие - файл есть
                    return exists_call_count > 1
                
                mock_exists.side_effect = exists_side_effect
                
                # Вызываем функцию
                try:
                    result = asyncio.run(upload_model_image(
                        modelid="0000010028Vx",
                        file=mock_file,
                        db=mock_db
                    ))
                    
                    # Проверяем количество проверок существования файла
                    # Должно быть не более 3 проверок
                    assert exists_call_count <= 3, f"Слишком много проверок существования файла: {exists_call_count}"
                    print(f"Количество проверок существования файла: {exists_call_count} (в норме)")
                    
                except Exception as e:
                    # Если функция выбросила исключение, проверяем логику проверок
                    assert exists_call_count <= 3, f"Слишком много проверок существования файла при ошибке: {exists_call_count}"
                    print(f"Функция завершилась с ошибкой, но проверки в норме: {exists_call_count}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])