import requests
import json

BASE_URL = "http://localhost:7990"

def test_modelgoods():
    print("Тестирование роутера modelgoods...")
    
    # Проверяем разные эндпоинты
    endpoints = [
        ("GET", "/api/modelgoods/", "Получение списка моделей"),
        ("GET", "/api/modelgoods/unsold/recent", "Непродающиеся товары"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"\n{description} ({method} {endpoint}):")
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", timeout=5)
            
            print(f"  Статус: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"  Получено записей: {len(data)}")
                        if len(data) > 0:
                            print(f"  Первая запись: {json.dumps(data[0], indent=2, ensure_ascii=False)[:200]}...")
                    else:
                        print(f"  Ответ: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"  Ответ получен (не JSON)")
            elif response.status_code == 404:
                print(f"  Эндпоинт не найден")
            elif response.status_code == 405:
                print(f"  Метод не поддерживается")
            elif response.status_code == 422:
                print(f"  Ошибка валидации")
        except Exception as e:
            print(f"  Ошибка: {e}")
    
    # Проверяем OpenAPI схему
    print("\nПроверка OpenAPI схемы...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get('paths', {})
            
            # Ищем пути с modelgoods
            modelgoods_paths = [path for path in paths if 'modelgoods' in path]
            print(f"  Всего путей с 'modelgoods': {len(modelgoods_paths)}")
            for path in modelgoods_paths:
                print(f"  - {path}")
        else:
            print(f"  Ошибка получения схемы: {response.status_code}")
    except Exception as e:
        print(f"  Ошибка: {e}")

if __name__ == "__main__":
    test_modelgoods()