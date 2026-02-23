import requests
import json
import time

BASE_URL = "http://localhost:7990"

def test_all_endpoints():
    print("Тестирование всех эндпоинтов API")
    print("=" * 60)
    
    # Даем серверу время на перезагрузку
    time.sleep(3)
    
    # 1. Проверка доступности сервера
    print("1. Проверка доступности сервера...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
        return
    
    # 2. Проверка OpenAPI схемы
    print("\n2. Проверка OpenAPI схемы...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get('paths', {})
            print(f"   Всего эндпоинтов: {len(paths)}")
            
            # Группируем эндпоинты по префиксам
            endpoints_by_prefix = {}
            for path in paths:
                if path.startswith('/api/'):
                    prefix = path.split('/')[2] if len(path.split('/')) > 2 else 'other'
                else:
                    prefix = 'root'
                
                if prefix not in endpoints_by_prefix:
                    endpoints_by_prefix[prefix] = []
                endpoints_by_prefix[prefix].append(path)
            
            print(f"   Группы эндпоинтов: {len(endpoints_by_prefix)}")
            for prefix, endpoints in sorted(endpoints_by_prefix.items()):
                print(f"   - {prefix}: {len(endpoints)} эндпоинтов")
                for endpoint in endpoints[:3]:  # Показываем первые 3
                    print(f"     * {endpoint}")
                if len(endpoints) > 3:
                    print(f"     ... и еще {len(endpoints) - 3}")
        else:
            print(f"   Ошибка: статус {response.status_code}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 3. Проверка ключевых эндпоинтов
    print("\n3. Проверка ключевых эндпоинтов...")
    
    test_endpoints = [
        ("GET", "/api/users/", "Пользователи"),
        ("GET", "/api/products/", "Товары"),
        ("GET", "/api/modelgoods/", "Модели товаров"),
        ("GET", "/api/modelgoods/search", "Поиск товаров"),
        ("GET", "/api/modelgoods/parameters", "Параметры товаров"),
        ("GET", "/api/ozon-categories/", "Категории Ozon"),
        ("POST", "/api/modelgoods/external-images/validate", "Валидация внешних изображений"),
        ("GET", "/api/modelgoods/external-images/", "Внешние изображения"),
    ]
    
    for method, endpoint, description in test_endpoints:
        print(f"   {description} ({method} {endpoint}):")
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            elif method == "POST":
                if endpoint.endswith("/validate"):
                    response = requests.post(
                        f"{BASE_URL}{endpoint}",
                        json={"url": "https://example.com/test.jpg"},
                        timeout=5
                    )
                else:
                    response = requests.post(f"{BASE_URL}{endpoint}", timeout=5)
            
            print(f"     Статус: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'total' in data:
                        print(f"     Всего записей: {data['total']}")
                except:
                    print(f"     Ответ получен")
            elif response.status_code == 404:
                print(f"     Эндпоинт не найден (возможно, требует параметров)")
            elif response.status_code == 405:
                print(f"     Метод не поддерживается")
            elif response.status_code == 422:
                print(f"     Ошибка валидации (ожидаемо для теста)")
        except Exception as e:
            print(f"     Ошибка: {e}")
    
    # 4. Проверка документации
    print("\n4. Проверка документации...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"   Swagger UI: {'Доступен' if response.status_code == 200 else 'Не доступен'}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("Тестирование завершено!")
    print("\nДля доступа к документации перейдите по адресу:")
    print(f"{BASE_URL}/docs")

if __name__ == "__main__":
    test_all_endpoints()