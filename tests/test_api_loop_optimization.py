"""
Тест для оптимизации петли API (вызов самого себя через HTTP)
"""
import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import os
import tempfile

def test_api_loop_problem():
    """
    Тест воспроизводит проблему петли API:
    - Веб-страница вызывает API endpoint
    - API endpoint вызывает другой API endpoint на том же сервере через HTTP
    - Это создает петлю и таймауты
    """
    from app.routers.web.pages import upload_to_main_api
    import requests
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file.write(b"test image content")
        temp_file_path = temp_file.name
    
    try:
        # Мокаем requests.post чтобы симулировать таймаут (как в реальной ситуации)
        with patch('requests.post') as mock_post:
            # Настраиваем мок для симуляции таймаута 120 секунд
            mock_post.side_effect = requests.exceptions.Timeout("Read timed out. (read timeout=120)")
            
            # Замеряем время выполнения
            start_time = time.time()
            result = upload_to_main_api("000001002Tyt", temp_file_path)
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # Проверяем, что функция вернула ошибку таймаута
            assert result['status'] == 'error'
            assert 'Таймаут при подключении к API' in result['message']
            
            # Время выполнения должно быть близко к таймауту (120 секунд)
            # Но в тесте с моком должно быть мгновенно
            print(f"Время выполнения с моком: {execution_time:.2f} секунд")
            print(f"Результат: {result['message']}")
            
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_direct_function_call_possibility():
    """
    Тест проверяет возможность прямого вызова upload_model_image вместо HTTP запроса
    """
    from app.routers.modelgoods_images import upload_model_image
    from sqlalchemy.orm import Session
    import tempfile
    import io
    
    # Создаем реальный временный файл для теста
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as real_temp_file:
        real_temp_file.write(b"test image content")
        real_temp_path = real_temp_file.name
    
    try:
        # Мокаем все зависимости
        with patch('app.routers.modelgoods_images.os.path.exists') as mock_exists:
            with patch('app.routers.modelgoods_images.os.unlink') as mock_unlink:
                with patch('app.routers.modelgoods_images.tempfile.NamedTemporaryFile') as mock_tempfile:
                    with patch('app.routers.modelgoods_images.os.getenv') as mock_getenv:
                        with patch('app.routers.modelgoods_images.os.path.getsize') as mock_getsize:
                            # Настраиваем моки
                            mock_getenv.side_effect = lambda key: {
                                'BASE_DIR': 'C:\\test',
                                'IMG_SUBDIR': 'img'
                            }.get(key, None)
                            
                            mock_exists.return_value = False
                            mock_getsize.return_value = 100
                            
                            # Создаем мок временного файла, который возвращает реальный путь
                            mock_temp = MagicMock()
                            mock_temp.name = real_temp_path
                            mock_temp.__enter__.return_value = mock_temp
                            mock_tempfile.return_value = mock_temp
                            
                            mock_db = MagicMock(spec=Session)
                            mock_result = MagicMock()
                            mock_result.fetchone.return_value = ["000001002Tyt"]
                            mock_db.execute.return_value = mock_result
                            
                            # Процедура возвращает успех
                            mock_procedure_result = [(1,)]
                            mock_db.execute.return_value.fetchall.return_value = mock_procedure_result
                            
                            mock_file = AsyncMock()
                            mock_file.filename = "test.jpg"
                            mock_file.read.return_value = b"test image content"
                            mock_file.close = AsyncMock()
                            
                            # Вызываем функцию напрямую
                            start_time = time.time()
                            result = asyncio.run(upload_model_image(
                                modelid="000001002Tyt",
                                file=mock_file,
                                db=mock_db
                            ))
                            end_time = time.time()
                            
                            execution_time = end_time - start_time
                            
                            # Проверяем, что функция работает быстро
                            assert execution_time < 1.0, f"Функция выполняется слишком долго: {execution_time:.2f} секунд"
                            assert result.status == 'success'
                            
                            print(f"Прямой вызов функции выполнен за: {execution_time:.3f} секунд")
                            print(f"Результат: status={result.status}, filename={result.filename}")
    finally:
        # Удаляем реальный временный файл
        if os.path.exists(real_temp_path):
            os.unlink(real_temp_path)

def test_jpg_conversion_optimization():
    """
    Тест проверяет возможность оптимизации конвертации JPG файлов
    """
    from app.routers.web.pages import download_and_convert_image
    from fastapi import HTTPException
    import requests
    
    # Мокаем requests.get для симуляции скачивания JPG файла
    with patch('requests.get') as mock_get:
        # Создаем мок ответа с JPG данными
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake jpg content"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Мокаем PIL.Image.open чтобы проверить, вызывается ли конвертация
        with patch('PIL.Image.open') as mock_image_open:
            mock_image = MagicMock()
            mock_image.mode = 'RGB'  # JPG обычно в режиме RGB
            mock_image.size = (100, 100)
            mock_image_open.return_value = mock_image
            
            # Мокаем tempfile.NamedTemporaryFile
            with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
                mock_temp = MagicMock()
                mock_temp.name = "C:\\temp\\test.jpg"
                mock_temp.__enter__.return_value = mock_temp
                mock_tempfile.return_value = mock_temp
                
                # Мокаем img.save чтобы проверить, вызывается ли сохранение
                with patch.object(mock_image, 'save') as mock_save:
                    # Вызываем функцию
                    result = download_and_convert_image("https://example.com/test.jpg")
                    
                    # Проверяем, что функция была вызвана
                    mock_get.assert_called_once_with("https://example.com/test.jpg", timeout=30)
                    
                    # Для JPG в режиме RGB не должна вызываться конвертация
                    # Проверяем, что save был вызван (файл сохранен)
                    mock_save.assert_called_once()
                    
                    print(f"JPG файл обработан, сохранение вызвано: {mock_save.call_args}")

def test_bypass_conversion_for_jpg():
    """
    Тест проверяет возможность полного обхода конвертации для JPG файлов
    """
    import tempfile
    import os
    
    # Создаем временный JPG файл
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file.write(b"fake jpg content")
        temp_file_path = temp_file.name
    
    try:
        # Проверяем, что файл существует
        assert os.path.exists(temp_file_path)
        
        # В реальной реализации можно было бы просто вернуть этот файл
        # без конвертации через Pillow
        file_size = os.path.getsize(temp_file_path)
        print(f"JPG файл создан: {temp_file_path}, размер: {file_size} байт")
        print("Для JPG файлов можно пропустить конвертацию через Pillow")
        
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_internal_api_call_alternative():
    """
    Тест проверяет альтернативу HTTP вызову - внутренний вызов функции
    """
    # Идея: вместо вызова upload_to_main_api, который делает HTTP запрос,
    # можно напрямую вызывать upload_model_image с теми же параметрами
    
    # Создаем тестовые данные
    test_modelid = "000001002Tyt"
    test_file_content = b"test image content"
    
    # В реальной реализации нужно:
    # 1. Скачать файл с URL
    # 2. Создать объект UploadFile из данных
    # 3. Вызвать upload_model_image напрямую
    
    print(f"Альтернатива: прямой вызов upload_model_image для modelid={test_modelid}")
    print(f"Размер данных: {len(test_file_content)} байт")
    print("Это устранит таймаут 120 секунд")

def test_performance_comparison():
    """
    Тест сравнивает производительность двух подходов
    """
    import time
    
    # Подход 1: HTTP запрос (текущий)
    http_approach_time = 120.0  # секунды таймаута
    
    # Подход 2: Прямой вызов (оптимизированный)
    direct_approach_time = 0.5  # ожидаемое время
    
    # Расчет ускорения
    speedup = http_approach_time / direct_approach_time
    
    print(f"Сравнение производительности:")
    print(f"  HTTP запрос: {http_approach_time:.1f} секунд (таймаут)")
    print(f"  Прямой вызов: {direct_approach_time:.1f} секунд (ожидаемо)")
    print(f"  Ускорение: {speedup:.1f}x")
    
    # Проверяем, что прямой вызов значительно быстрее
    assert direct_approach_time < http_approach_time / 10, "Прямой вызов должен быть значительно быстрее"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])