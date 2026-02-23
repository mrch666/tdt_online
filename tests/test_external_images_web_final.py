"""
Финальный тест для веб-страницы управления внешними изображениями
Проверяет полную функциональность
"""
import sys
import os
sys.path.insert(0, '.')

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_web_page_route():
    """Тест 1: Проверка доступности веб-страницы"""
    print("\nТест 1: Проверка доступности веб-страницы")
    
    # Мокируем базу данных
    with patch('app.routers.web.pages.get_db') as mock_get_db:
        mock_session = MagicMock()
        mock_query = MagicMock()
        
        # Настраиваем моки
        mock_session.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        mock_query.all.return_value = []  # Пустой список товаров
        
        mock_get_db.return_value = mock_session
        
        # Тестируем маршрут
        response = client.get("/web/external-images/")
        
        print(f"  Статус ответа: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('content-type')}")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get('content-type', '')
        
        # Проверяем, что страница содержит основные элементы
        html_content = response.text
        assert "Внешние изображения товаров" in html_content
        assert "Показать скрытые товары" in html_content
        
        print("  OK: Веб-страница доступна и содержит основные элементы")
        return True

def test_web_page_with_show_hidden():
    """Тест 2: Проверка параметра show_hidden"""
    print("\nТест 2: Проверка параметра show_hidden")
    
    with patch('app.routers.web.pages.get_db') as mock_get_db:
        mock_session = MagicMock()
        mock_query = MagicMock()
        
        mock_session.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        mock_query.all.return_value = []
        
        mock_get_db.return_value = mock_session
        
        # Тестируем с параметром show_hidden
        response = client.get("/web/external-images/?show_hidden=true")
        
        print(f"  Статус ответа: {response.status_code}")
        assert response.status_code == 200
        
        print("  OK: Параметр show_hidden обрабатывается корректно")
        return True

def test_process_image_endpoint():
    """Тест 3: Проверка endpoint'а обработки изображения"""
    print("\nТест 3: Проверка endpoint'а обработки изображения")
    
    with patch('app.routers.web.pages.get_db') as mock_get_db, \
         patch('app.routers.web.pages.download_and_convert_image') as mock_download, \
         patch('app.routers.web.pages.upload_to_main_api') as mock_upload:
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_image = MagicMock()
        
        # Настраиваем моки
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_image
        
        # Настраиваем мок изображения
        mock_image.id = "test_image_123"
        mock_image.modelid = "000001001G2C"
        mock_image.url = "https://example.com/test.jpg"
        mock_image.is_approved = 0
        mock_image.is_loaded_to_db = 0
        
        mock_get_db.return_value = mock_session
        
        # Настраиваем моки для функций обработки
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/test_image.jpg"
        mock_download.return_value = mock_temp_file
        mock_upload.return_value = {"status": "success"}
        
        # Тестируем endpoint
        response = client.post("/web/external-images/test_image_123/process")
        
        print(f"  Статус ответа: {response.status_code}")
        print(f"  Ответ JSON: {response.json()}")
        
        assert response.status_code == 200
        result = response.json()
        assert "success" in result
        
        print("  OK: Endpoint обработки изображения работает")
        return True

def test_process_image_not_found():
    """Тест 4: Проверка обработки несуществующего изображения"""
    print("\nТест 4: Проверка обработки несуществующего изображения")
    
    with patch('app.routers.web.pages.get_db') as mock_get_db:
        mock_session = MagicMock()
        mock_query = MagicMock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = None  # Изображение не найдено
        
        mock_get_db.return_value = mock_session
        
        response = client.post("/web/external-images/nonexistent_image/process")
        
        print(f"  Статус ответа: {response.status_code}")
        assert response.status_code == 404
        
        result = response.json()
        assert result["success"] == False
        assert "не найдено" in result["message"].lower()
        
        print("  OK: Корректная обработка несуществующего изображения")
        return True

def test_process_image_already_approved():
    """Тест 5: Проверка обработки уже подтвержденного изображения"""
    print("\nТест 5: Проверка обработки уже подтвержденного изображения")
    
    with patch('app.routers.web.pages.get_db') as mock_get_db:
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_image = MagicMock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_image
        
        # Изображение уже подтверждено
        mock_image.id = "test_image_456"
        mock_image.is_approved = 1
        
        mock_get_db.return_value = mock_session
        
        response = client.post("/web/external-images/test_image_456/process")
        
        print(f"  Статус ответа: {response.status_code}")
        assert response.status_code == 400
        
        result = response.json()
        assert result["success"] == False
        assert "уже подтверждено" in result["message"].lower()
        
        print("  OK: Корректная обработка уже подтвержденного изображения")
        return True

def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ВЕБ-СТРАНИЦЫ ВНЕШНИХ ИЗОБРАЖЕНИЙ")
    print("=" * 60)
    
    all_passed = True
    
    try:
        # Запускаем все тесты
        tests = [
            ("Доступность веб-страницы", test_web_page_route),
            ("Параметр show_hidden", test_web_page_with_show_hidden),
            ("Endpoint обработки изображения", test_process_image_endpoint),
            ("Несуществующее изображение", test_process_image_not_found),
            ("Уже подтвержденное изображение", test_process_image_already_approved),
        ]
        
        for test_name, test_func in tests:
            print(f"\nЗапуск теста: {test_name}")
            try:
                if test_func():
                    print(f"  PASS: {test_name}")
                else:
                    print(f"  FAIL: {test_name}")
                    all_passed = False
            except Exception as e:
                print(f"  ERROR: {test_name} - {str(e)}")
                import traceback
                traceback.print_exc()
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("\nВеб-страница управления внешними изображениями готова к использованию.")
            print("Доступна по адресу: http://localhost:7990/web/external-images/")
        else:
            print("НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
            print("Требуется дополнительная отладка.")
        
        print("=" * 60)
        
        return all_passed
        
    except Exception as e:
        print(f"\nОшибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)