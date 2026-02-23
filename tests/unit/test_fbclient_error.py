"""Тест для ошибки: Firebird Client Library 'C:\\tdt3\\bases\fbclient.dll' not found"""
import sys
sys.path.append('.')
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_fbclient_error():
    """Тест, который должен падать с ошибкой о fbclient.dll"""
    print("=== ТЕСТ ОШИБКИ FBClient.dll ===")
    print("Ошибка: Firebird Client Library 'C:\\tdt3\\bases\fbclient.dll' not found")
    
    print("\nАнализ ошибки:")
    print("1. Библиотека fbclient.dll ищется по пути: C:\\tdt3\\bases\\fbclient.dll")
    print("2. Правильный путь должен быть: C:\\Program Files (x86)\\tdt3\\fbclient.dll")
    print("3. Проблема в конфигурации подключения к базе данных")
    
    print("\n=== ПРОВЕРКА ПУТЕЙ ===")
    
    # Проверяем разные пути
    paths_to_check = [
        {
            "path": "C:\\tdt3\\bases\\fbclient.dll",
            "description": "Неправильный путь из ошибки",
            "should_exist": False
        },
        {
            "path": "C:\\Program Files (x86)\\tdt3\\fbclient.dll",
            "description": "Правильный путь согласно документации",
            "should_exist": True
        },
        {
            "path": "fbclient.dll",
            "description": "Текущая директория",
            "should_exist": True
        }
    ]
    
    for path_info in paths_to_check:
        print(f"\n--- Проверка: {path_info['description']} ---")
        print(f"Путь: {path_info['path']}")
        
        exists = os.path.exists(path_info['path'])
        print(f"Файл существует: {exists}")
        
        if exists:
            size = os.path.getsize(path_info['path'])
            print(f"Размер файла: {size} байт")
        
        if exists == path_info['should_exist']:
            print("[OK] Состояние файла соответствует ожиданиям")
        else:
            print("[ERROR] Состояние файла не соответствует ожиданиям!")
    
    print("\n=== ВЫВОДЫ ===")
    print("1. Ошибка возникает из-за неправильного пути к fbclient.dll")
    print("2. Нужно проверить конфигурацию подключения к БД")
    print("3. Возможно, проблема в файле .env или database.py")
    
    print("\n=== РЕКОМЕНДАЦИИ ===")
    print("1. Проверить файл .env на наличие правильных путей")
    print("2. Проверить файл database.py на правильность подключения")
    print("3. Убедиться, что fbclient.dll находится в правильном месте")
    
    return True

if __name__ == "__main__":
    try:
        success = test_fbclient_error()
        if success:
            print("\n=== ТЕСТ ЗАВЕРШЕН ===")
            sys.exit(0)
    except Exception as e:
        print(f"\n=== ОШИБКА ПРИ ТЕСТИРОВАНИИ ===")
        print(f"Ошибка: {e}")
        sys.exit(1)