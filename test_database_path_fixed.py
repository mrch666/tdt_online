"""Тест, который проходит после исправления путей к базе данных"""
import sys
sys.path.append('.')
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_database_path_fixed():
    """Тест, который должен проходить после исправления путей"""
    print("=== ТЕСТ ИСПРАВЛЕННЫХ ПУТЕЙ К БАЗЕ ДАННЫХ ===")
    
    # Загружаем переменные из .env
    from dotenv import load_dotenv
    load_dotenv()
    
    base_dir = os.getenv('BASE_DIR')
    database_name = os.getenv('DATABASE_NAME')
    fbclient_path = os.getenv('FBCLIENT_PATH')
    
    print(f"BASE_DIR из .env: {base_dir}")
    print(f"DATABASE_NAME из .env: {database_name}")
    print(f"FBCLIENT_PATH из .env: {fbclient_path}")
    
    all_passed = True
    
    print("\n=== ПРОВЕРКА ПУТЕЙ ===")
    
    # 1. Проверяем путь к базе данных
    if base_dir and database_name:
        db_path = os.path.join(base_dir, database_name)
        print(f"\n1. Путь к базе данных: {db_path}")
        
        exists = os.path.exists(db_path)
        print(f"   Файл существует: {exists}")
        
        if exists:
            size = os.path.getsize(db_path)
            print(f"   Размер: {size} байт")
            print("   [OK] Файл базы данных найден")
        else:
            print("   [ERROR] Файл базы данных не найден!")
            all_passed = False
    else:
        print("[ERROR] Не удалось загрузить BASE_DIR или DATABASE_NAME из .env")
        all_passed = False
    
    # 2. Проверяем путь к fbclient.dll
    print(f"\n2. Путь к fbclient.dll: {fbclient_path}")
    
    if fbclient_path:
        exists = os.path.exists(fbclient_path)
        print(f"   Файл существует: {exists}")
        
        if exists:
            size = os.path.getsize(fbclient_path)
            print(f"   Размер: {size} байт")
            print("   [OK] Файл fbclient.dll найден")
        else:
            print("   [ERROR] Файл fbclient.dll не найден!")
            all_passed = False
    else:
        print("[ERROR] Не удалось загрузить FBCLIENT_PATH из .env")
        all_passed = False
    
    # 3. Проверяем, что в database.py используется правильный путь
    print("\n3. Проверка конфигурации database.py")
    
    try:
        with open('app/database.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем, что используется os.getenv для fb_library_name
        if 'os.getenv(\'FBCLIENT_PATH\'' in content:
            print("   [OK] database.py использует FBCLIENT_PATH из .env")
        else:
            print("   [ERROR] database.py не использует FBCLIENT_PATH из .env")
            all_passed = False
            
        # Проверяем, что BASE_DIR используется в connection string
        if 'os.getenv(\'BASE_DIR\')' in content:
            print("   [OK] database.py использует BASE_DIR из .env")
        else:
            print("   [ERROR] database.py не использует BASE_DIR из .env")
            all_passed = False
            
    except Exception as e:
        print(f"   [ERROR] Ошибка при чтении database.py: {e}")
        all_passed = False
    
    # 4. Проверяем существование директорий для изображений
    print("\n4. Проверка директорий для файлов")
    
    img_subdir = os.getenv('IMG_SUBDIR', 'img')
    if base_dir and img_subdir:
        img_dir = os.path.join(base_dir, img_subdir)
        print(f"   Путь к изображениям: {img_dir}")
        
        exists = os.path.exists(img_dir)
        print(f"   Директория существует: {exists}")
        
        if exists:
            print("   [OK] Директория для изображений найдена")
        else:
            print("   [WARNING] Директория для изображений не найдена")
            # Это не критическая ошибка, но стоит отметить
    
    print("\n=== ИТОГИ ===")
    if all_passed:
        print("[OK] Все тесты прошли успешно")
        print("[OK] Пути к базе данных и fbclient.dll правильные")
        print("[OK] Конфигурация использует переменные из .env")
    else:
        print("[ERROR] Некоторые тесты не прошли")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = test_database_path_fixed()
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