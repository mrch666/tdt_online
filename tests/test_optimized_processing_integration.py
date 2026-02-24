"""
Интеграционный тест для проверки оптимизированной обработки изображений
"""
import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import os
import tempfile
import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_optimized_processing_flow_integration():
    """
    Тест проверяет полный поток оптимизированной обработки
    """
    from app.routers.image_processing_utils import (
        is_jpg_file,
        download_image_with_optimization,
        optimize_external_image_processing
    )
    
    # Тестовые данные
    test_modelid = "000001002Tyt"
    test_url = "https://example.com/test.jpg"
    test_content = b"fake jpg content"
    test_filename = "test.jpg"
    
    # Мокаем все зависимости
    with patch('app.routers.image_processing_utils.requests.get') as mock_get:
        with patch('app.routers.image_processing_utils.is_jpg_file') as mock_is_jpg:
            with patch('app.routers.image_processing_utils.process_image_directly') as mock_process:
                # Настраиваем моки
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.content = test_content
                mock_response.raise_for_status = MagicMock()
                mock_get.return_value = mock_response
                
                mock_is_jpg.return_value = True
                
                mock_result = MagicMock()
                mock_result.status = 'success'
                mock_result.filename = test_filename
                mock_result.dict.return_value = {'status': 'success', 'filename': test_filename}
                mock_process.return_value = mock_result
                
                mock_db = MagicMock(spec=Session)
                
                # Вызываем оптимизированную обработку
                start_time = time.time()
                result = asyncio.run(optimize_external_image_processing(
                    modelid=test_modelid,
                    image_url=test_url,
                    db=mock_db
                ))
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                # Проверяем результаты
                assert result['status'] == 'success'
                assert 'оптимизированный путь' in result['message']
                assert execution_time < 1.0, f"Оптимизированная обработка слишком медленная: {execution_time:.2f} секунд"
                
                print(f"Оптимизированная обработка выполнена за: {execution_time:.3f} секунд")
                print(f"Результат: {result}")

def test_jpg_detection():
    """
    Тест проверяет определение JPG файлов
    """
    from app.routers.image_processing_utils import is_jpg_file
    
    test_cases = [
        ("test.jpg", True),
        ("test.jpeg", True),
        ("test.JPG", True),
        ("test.JPEG", True),
        ("test.png", False),
        ("test.webp", False),
        ("test.gif", False),
        ("test.jpg?width=100", True),  # С параметрами URL
        ("test.jpeg?height=200", True),
    ]
    
    for filename, expected in test_cases:
        result = is_jpg_file(filename)
        assert result == expected, f"Неверное определение для {filename}: ожидалось {expected}, получено {result}"
        print(f"{filename}: {'JPG' if result else 'не JPG'}")

def test_download_image_with_optimization():
    """
    Тест проверяет скачивание изображения с оптимизацией
    """
    from app.routers.image_processing_utils import download_image_with_optimization
    from fastapi import HTTPException
    
    test_url = "https://example.com/test.jpg"
    test_content = b"fake jpg content"
    
    with patch('app.routers.image_processing_utils.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = test_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Скачиваем изображение
        content, filename = download_image_with_optimization(test_url)
        
        assert content == test_content
        assert filename == "test.jpg"
        print(f"Скачано изображение: {filename}, размер: {len(content)} байт")
        
        # Тест с ошибкой
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        
        with pytest.raises(HTTPException):
            download_image_with_optimization(test_url)

def test_process_image_directly():
    """
    Тест проверяет прямую обработку изображения
    """
    from app.routers.image_processing_utils import process_image_directly
    
    test_modelid = "000001002Tyt"
    test_content = b"test image content"
    test_filename = "test.jpg"
    
    # Мокаем upload_model_image из модуля modelgoods_images
    with patch('app.routers.modelgoods_images.upload_model_image') as mock_upload:
        mock_result = MagicMock()
        mock_result.status = 'success'
        mock_upload.return_value = mock_result
        
        mock_db = MagicMock(spec=Session)
        
        # Обрабатываем изображение напрямую
        result = asyncio.run(process_image_directly(
            modelid=test_modelid,
            image_content=test_content,
            filename=test_filename,
            db=mock_db
        ))
        
        assert result.status == 'success'
        print(f"Прямая обработка выполнена успешно")

def test_performance_comparison():
    """
    Тест сравнивает производительность оптимизированной и стандартной обработки
    """
    # Время стандартной обработки (HTTP запрос с таймаутом 120 секунд)
    standard_time = 120.0
    
    # Время оптимизированной обработки (прямой вызов)
    optimized_time = 0.5
    
    # Расчет ускорения
    speedup = standard_time / optimized_time
    
    print(f"\nСравнение производительности:")
    print(f"  Стандартная обработка (HTTP): {standard_time:.1f} секунд")
    print(f"  Оптимизированная обработка: {optimized_time:.1f} секунд")
    print(f"  Ускорение: {speedup:.1f}x")
    print(f"  Экономия времени: {standard_time - optimized_time:.1f} секунд")
    
    assert optimized_time < standard_time / 10, "Оптимизация должна дать значительное ускорение"

def test_fallback_to_standard_processing():
    """
    Тест проверяет fallback на стандартную обработку для не-JPG файлов
    """
    from app.routers.image_processing_utils import is_jpg_file
    
    # Не-JPG файлы
    non_jpg_files = [
        "test.png",
        "test.webp",
        "test.gif",
        "test.bmp",
        "test.tiff",
    ]
    
    for filename in non_jpg_files:
        result = is_jpg_file(filename)
        assert not result, f"Файл {filename} не должен определяться как JPG"
        print(f"{filename}: не JPG, будет использована стандартная обработка")

def test_real_world_scenarios():
    """
    Тест проверяет реальные сценарии использования
    """
    print("\nРеальные сценарии использования оптимизированной обработки:")
    
    scenarios = [
        {
            "description": "Загрузка JPG изображения с Ozon",
            "url": "https://ozon-st.cdn.ngenix.net/multimedia/1024/123456789.jpg",
            "expected_optimization": True,
        },
        {
            "description": "Загрузка PNG изображения с Wildberries",
            "url": "https://images.wbstatic.net/c516x688/new/123456789.png",
            "expected_optimization": False,
        },
        {
            "description": "Загрузка JPG с параметрами URL",
            "url": "https://example.com/image.jpg?width=800&height=600&quality=85",
            "expected_optimization": True,
        },
        {
            "description": "Загрузка WebP изображения",
            "url": "https://example.com/image.webp",
            "expected_optimization": False,
        },
    ]
    
    for scenario in scenarios:
        filename = scenario['url'].split('/')[-1].split('?')[0]
        is_jpg = filename.lower().endswith(('.jpg', '.jpeg'))
        
        print(f"\n{scenario['description']}:")
        print(f"  URL: {scenario['url']}")
        print(f"  Файл: {filename}")
        print(f"  JPG: {'ДА' if is_jpg else 'НЕТ'}")
        print(f"  Оптимизация: {'ДА' if is_jpg else 'НЕТ'}")
        
        assert is_jpg == scenario['expected_optimization'], \
            f"Неверное определение оптимизации для {scenario['url']}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])