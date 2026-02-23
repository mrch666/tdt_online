"""Тест, который проходит после исправления пути к fbclient.dll"""
import sys
sys.path.append('.')
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_fbclient_fixed():
    """Тест, который должен проходить после исправления пути"""
    print("=== ТЕСТ ИСПРАВЛЕННОГО ПУТИ FBClient.dll ===")
    print("Цель: проверить, что путь к fbclient.dll правильный")
    
    print("\n=== ПРОВЕРКА ПУТЕЙ ===")
    
    # Правильные пути
    correct_paths = [
        {
            "path": "C:\\Program Files (x86)\\tdt3\\fbclient.dll",
            "description": "Правильный путь согласно документации",
            "should_exist": True
        },
        {
            "path": "fbclient.dll",
            "description": "Текущая директория (резервный вариант)",
            "should_exist": True
        }
    ]
    
    # Неправильные пути
    incorrect_paths = [
        {
            "path": "C:\\tdt3\\bases\\fbclient.dll",
            "description": "Старый неправильный путь",
            "should_exist": False
        }
    ]
    
    all_passed = True
    
    print("\n--- Проверка правильных путей ---")
    for path_info in correct_paths:
        print(f"\nПуть: {path_info['path']}")
        print(f"Описание: {path_info['description']}")
        
        exists = os.path.exists(path_info['path'])
        print(f"Файл существует: {exists}")
        
        if exists:
            size = os.path.getsize(path_info['path'])
            print(f"Размер файла: {size} байт")
            
            if size > 0:
                print("[OK] Файл существует и имеет ненулевой размер")
            else:
                print("[ERROR] Файл существует, но имеет нулевой размер")
                all_passed = False
        else:
            print("[ERROR] Файл не существует!")
            all_passed = False
    
    print("\n--- Проверка неправильных путей ---")
    for path_info in incorrect_paths:
        print(f"\nПуть: {path_info['path']}")
        print(f"Описание: {path_info['description']}")
        
        exists = os.path.exists(path_info['path'])
        print(f"Файл существует: {exists}")
        
        if not exists:
            print("[OK] Файл не существует (как и должно быть)")
        else:
            print("[WARNING] Файл существует, но не должен")
            # Это не критическая ошибка, но странно
    
    print("\n=== ПРОВЕРКА КОНФИГУРАЦИИ ===")
    
    # Проверяем, что в database.py правильный путь
    try:
        with open('app/database.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '"fb_library_name": "C:\\\\Program Files (x86)\\\\tdt3\\\\fbclient.dll"' in content:
            print("[OK] В database.py установлен правильный путь к fbclient.dll")
        else:
            print("[ERROR] В database.py неправильный путь к fbclient.dll")
            all_passed = False
            
    except Exception as e:
        print(f"[ERROR] Ошибка при чтении database.py: {e}")
        all_passed = False
    
    print("\n=== ИТОГИ ===")
    if all_passed:
        print("[OK] Все тесты прошли успешно")
        print("[OK] Путь к fbclient.dll правильный")
        print("[OK] Файл fbclient.dll существует и доступен")
    else:
        print("[ERROR] Некоторые тесты не прошли")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = test_fbclient_fixed()
        if success:
            print("\n=== ТЕСТ ЗАВЕРШЕН УСПЕШНО ===")
            sys.exit(0)
        else:
            print("\n=== ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ ===")
            sys.exit(1)
    except Exception as e:
        print(f"\n=== НЕОЖИДАННАЯ ОШИБКА ===")
        print(f"Ошибка: {e}")
        sys.exit(1)