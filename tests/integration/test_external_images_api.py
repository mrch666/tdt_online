#!/usr/bin/env python
"""
Тестовый скрипт для проверки API внешних изображений
"""
import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:7990"
API_PREFIX = "/api/modelgoods/external-images"

def print_response(response: requests.Response, description: str):
    """Печать ответа API"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)

def test_validate_image():
    """Тест валидации изображения"""
    print("\n1. Тест валидации изображения")
    
    # Пример валидного URL (замените на реальный)
    valid_url = "https://example.com/image.jpg"
    
    # Пример невалидного URL
    invalid_url = "https://example.com/image.png"
    
    # Тест валидного URL
    payload = {"url": valid_url}
    response = requests.post(f"{BASE_URL}{API_PREFIX}/validate", json=payload)
    print_response(response, "Валидация валидного URL")
    
    # Тест невалидного URL
    payload = {"url": invalid_url}
    response = requests.post(f"{BASE_URL}{API_PREFIX}/validate", json=payload)
    print_response(response, "Валидация невалидного URL (PNG)")

def test_create_external_image():
    """Тест создания записи о внешнем изображении"""
    print("\n2. Тест создания записи о внешнем изображении")
    
    # Тестовые данные
    test_data = {
        "modelid": "000001002Qa{",  # Пример modelid (12 символов)
        "url": "https://example.com/test-image.jpg",
        "userid": "0"
    }
    
    response = requests.post(f"{BASE_URL}{API_PREFIX}/", json=test_data)
    print_response(response, "Создание записи о внешнем изображении")
    
    if response.status_code == 201:
        return response.json()["id"]
    return None

def test_get_external_images(image_id: str = None):
    """Тест получения внешних изображений"""
    print("\n3. Тест получения внешних изображений")
    
    # Получение всех изображений
    response = requests.get(f"{BASE_URL}{API_PREFIX}/")
    print_response(response, "Получение всех внешних изображений")
    
    # Получение изображений по modelid
    modelid = "000001002Qa{"
    response = requests.get(f"{BASE_URL}{API_PREFIX}/{modelid}")
    print_response(response, f"Получение внешних изображений для modelid={modelid}")
    
    # Получение с фильтрами
    params = {
        "is_approved": 0,
        "is_loaded_to_db": 0
    }
    response = requests.get(f"{BASE_URL}{API_PREFIX}/{modelid}", params=params)
    print_response(response, f"Получение с фильтрами (не одобренные, не загруженные)")

def test_update_external_image(image_id: str):
    """Тест обновления статусов изображения"""
    print("\n4. Тест обновления статусов изображения")
    
    if not image_id:
        print("Нет image_id для теста обновления")
        return
    
    # Обновление статуса одобрения
    update_data = {
        "is_approved": 1
    }
    
    response = requests.put(f"{BASE_URL}{API_PREFIX}/{image_id}", json=update_data)
    print_response(response, f"Обновление статуса одобрения для image_id={image_id}")
    
    # Обновление статуса загрузки в БД
    update_data = {
        "is_loaded_to_db": 1
    }
    
    response = requests.put(f"{BASE_URL}{API_PREFIX}/{image_id}", json=update_data)
    print_response(response, f"Обновление статуса загрузки в БД для image_id={image_id}")

def test_delete_external_image(image_id: str):
    """Тест удаления изображения"""
    print("\n5. Тест удаления изображения")
    
    if not image_id:
        print("Нет image_id для теста удаления")
        return
    
    response = requests.delete(f"{BASE_URL}{API_PREFIX}/{image_id}")
    print_response(response, f"Удаление изображения image_id={image_id}")

def test_api_documentation():
    """Проверка документации API"""
    print("\n6. Проверка документации API")
    
    # Проверка Swagger UI
    response = requests.get(f"{BASE_URL}/docs")
    print(f"\nSwagger UI доступен: {response.status_code == 200}")
    
    # Проверка OpenAPI схемы
    response = requests.get(f"{BASE_URL}/openapi.json")
    print(f"OpenAPI схема доступна: {response.status_code == 200}")

def main():
    """Основная функция тестирования"""
    print("Тестирование API внешних изображений")
    print(f"Базовый URL: {BASE_URL}")
    
    try:
        # Проверяем доступность сервера
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"Сервер не доступен. Status Code: {response.status_code}")
            print("Запустите сервер командой: uvicorn app.main:app --reload --port 7990")
            sys.exit(1)
        
        # Запускаем тесты
        test_validate_image()
        
        image_id = test_create_external_image()
        
        if image_id:
            test_get_external_images(image_id)
            test_update_external_image(image_id)
            test_get_external_images(image_id)  # Проверяем после обновления
            test_delete_external_image(image_id)
            test_get_external_images(image_id)  # Проверяем после удаления
        
        test_api_documentation()
        
        print("\n" + "="*60)
        print("Тестирование завершено!")
        
    except requests.exceptions.ConnectionError:
        print(f"\nОшибка подключения к серверу {BASE_URL}")
        print("Убедитесь, что сервер запущен командой:")
        print("uvicorn app.main:app --reload --port 7990")
        sys.exit(1)
    except Exception as e:
        print(f"\nОшибка при тестировании: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()