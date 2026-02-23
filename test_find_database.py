"""Тест для поиска файла базы данных"""
import sys
sys.path.append('.')
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_find_database():
    """Поиск файла базы данных в разных местах"""
    print("=== ПОИСК ФАЙЛА БАЗЫ ДАННЫХ ===")
    
    # Возможные места расположения базы данных
    possible_paths = [
        # Пути из .env
        "C:\\tdt3\\bases\\TDTBASE.FDB",
        "C:\\tdt3\\bases\\TDTBASE_TEST.FDB",
        
        # Альтернативные пути
        "C:\\Program Files (x86)\\tdt3\\bases\\TDTBASE.FDB",
        "C:\\Program Files (x86)\\tdt3\\bases\\TDTBASE_TEST.FDB",
        "C:\\Program Files (x86)\\tdt3\\TDTBASE.FDB",
        
        # Текущая директория
        "TDTBASE.FDB",
        "TDTBASE_TEST.FDB",
        
        # Другие возможные пути
        "d:\\Python Projects\\fastapi\\TDTBASE.FDB",
        "d:\\Python Projects\\fastapi\\TDTBASE_TEST.FDB",
    ]
    
    found_paths = []
    
    for path in possible_paths:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"[FOUND] {path} - {size} байт")
            found_paths.append((path, size))
        else:
            print(f"[NOT FOUND] {path}")
    
    print("\n=== РЕЗУЛЬТАТЫ ПОИСКА ===")
    if found_paths:
        print(f"Найдено {len(found_paths)} файлов базы данных:")
        for path, size in found_paths:
            print(f"  - {path} ({size} байт)")
    else:
        print("Файлы базы данных не найдены!")
        
        # Проверяем существование родительских директорий
        print("\n=== ПРОВЕРКА ДИРЕКТОРИЙ ===")
        directories_to_check = [
            "C:\\tdt3\\bases",
            "C:\\Program Files (x86)\\tdt3\\bases",
            "C:\\Program Files (x86)\\tdt3",
            "d:\\Python Projects\\fastapi"
        ]
        
        for directory in directories_to_check:
            if os.path.exists(directory):
                print(f"Директория существует: {directory}")
                try:
                    files = os.listdir(directory)
                    print(f"  Содержит {len(files)} файлов/папок")
                    for file in files[:5]:  # Показываем первые 5
                        print(f"    - {file}")
                    if len(files) > 5:
                        print(f"    ... и еще {len(files) - 5}")
                except Exception as e:
                    print(f"  Ошибка при чтении: {e}")
            else:
                print(f"Директория не существует: {directory}")
    
    print("\n=== ВЫВОДЫ ===")
    if found_paths:
        print("1. Файл базы данных найден в другом месте")
        print("2. Нужно обновить .env или логику поиска")
        print("3. Можно создать симлинк или скопировать файл")
    else:
        print("1. Файл базы данных не найден нигде")
        print("2. Нужно создать базу данных или найти ее расположение")
        print("3. Проверить настройки Firebird Server")
    
    return bool(found_paths)

if __name__ == "__main__":
    try:
        found = test_find_database()
        if found:
            print("\n=== ФАЙЛ БАЗЫ ДАННЫХ НАЙДЕН ===")
            sys.exit(0)
        else:
            print("\n=== ФАЙЛ БАЗЫ ДАННЫХ НЕ НАЙДЕН ===")
            sys.exit(1)
    except Exception as e:
        print(f"\n=== ОШИБКА ПРИ ПОИСКЕ ===")
        print(f"Ошибка: {e}")
        sys.exit(1)