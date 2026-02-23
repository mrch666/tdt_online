"""Тест для ошибки: файл базы данных не найден"""
import sys
sys.path.append('.')
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_database_path_error():
    """Тест для проверки путей к базе данных"""
    print("=== ТЕСТ ОШИБКИ ПУТИ К БАЗЕ ДАННЫХ ===")
    print("Ошибка: Не удается найти указанный файл C:\\\\tdt3\\\\bases/TDTBASE.FDB")
    
    print("\n=== ПРОВЕРКА ПУТЕЙ ===")
    
    # Загружаем переменные из .env
    from dotenv import load_dotenv
    load_dotenv()
    
    base_dir = os.getenv('BASE_DIR')
    database_name = os.getenv('DATABASE_NAME')
    
    print(f"BASE_DIR из .env: {base_dir}")
    print(f"DATABASE_NAME из .env: {database_name}")
    
    if base_dir and database_name:
        # Формируем путь к базе данных
        db_path = os.path.join(base_dir, database_name)
        print(f"\nПуть к базе данных: {db_path}")
        
        # Проверяем существование
        exists = os.path.exists(db_path)
        print(f"Файл базы данных существует: {exists}")
        
        if exists:
            size = os.path.getsize(db_path)
            print(f"Размер файла базы данных: {size} байт")
        else:
            print("[ERROR] Файл базы данных не найден!")
            
            # Проверяем существование директории
            dir_exists = os.path.exists(base_dir)
            print(f"Директория {base_dir} существует: {dir_exists}")
            
            if dir_exists:
                print("Содержимое директории:")
                try:
                    files = os.listdir(base_dir)
                    for file in files[:10]:  # Показываем первые 10 файлов
                        print(f"  - {file}")
                    if len(files) > 10:
                        print(f"  ... и еще {len(files) - 10} файлов")
                except Exception as e:
                    print(f"Ошибка при чтении директории: {e}")
    else:
        print("[ERROR] Не удалось загрузить переменные из .env")
    
    print("\n=== ПРОВЕРКА FBClient.dll ===")
    
    # Проверяем правильный путь к fbclient.dll
    fbclient_paths = [
        "C:\\Program Files (x86)\\tdt3\\fbclient.dll",
        os.path.join(base_dir, "fbclient.dll") if base_dir else None,
        "fbclient.dll"
    ]
    
    for path in fbclient_paths:
        if path:
            print(f"\nПуть: {path}")
            exists = os.path.exists(path)
            print(f"Файл существует: {exists}")
            
            if exists:
                size = os.path.getsize(path)
                print(f"Размер: {size} байт")
    
    print("\n=== ВЫВОДЫ ===")
    print("1. Пути должны формироваться из .env файла")
    print("2. BASE_DIR используется для путей к базам данных")
    print("3. fbclient.dll должен быть в правильном месте")
    print("4. Нужно проверить существование файла базы данных")
    
    return True

if __name__ == "__main__":
    try:
        success = test_database_path_error()
        if success:
            print("\n=== ТЕСТ ЗАВЕРШЕН ===")
            sys.exit(0)
    except Exception as e:
        print(f"\n=== ОШИБКА ПРИ ТЕСТИРОВАНИИ ===")
        print(f"Ошибка: {e}")
        sys.exit(1)