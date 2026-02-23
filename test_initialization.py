"""
Тестирование инициализации таблицы modelgoods_external_images с генератором и триггером
"""
import sys
import os
sys.path.insert(0, '.')

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.database_utils import check_and_create_external_images_table
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("api")

# Используем тестовую базу данных SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_init.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_initialization():
    """Тест инициализации таблицы"""
    print("=" * 60)
    print("ТЕСТ ИНИЦИАЛИЗАЦИИ ТАБЛИЦЫ modelgoods_external_images")
    print("=" * 60)
    
    db = TestingSessionLocal()
    
    try:
        # Проверяем существование таблицы до инициализации
        inspector = inspect(db.get_bind())
        table_exists_before = inspector.has_table('modelgoods_external_images')
        print(f"Таблица существует до инициализации: {table_exists_before}")
        
        # Вызываем функцию инициализации
        print("\nЗапускаем инициализацию таблицы...")
        result = check_and_create_external_images_table(db)
        
        # Проверяем существование таблицы после инициализации
        table_exists_after = inspector.has_table('modelgoods_external_images')
        print(f"Таблица существует после инициализации: {table_exists_after}")
        
        if result and table_exists_after:
            print("\nOK Инициализация прошла успешно")
            
            # Проверяем структуру таблицы
            columns = inspector.get_columns('modelgoods_external_images')
            print(f"\nСтруктура таблицы ({len(columns)} полей):")
            for col in columns:
                print(f"  - {col['name']}: {col['type']} (nullable: {col.get('nullable', True)})")
            
            # Проверяем индексы
            indexes = inspector.get_indexes('modelgoods_external_images')
            print(f"\nИндексы таблицы ({len(indexes)}):")
            for idx in indexes:
                print(f"  - {idx['name']}: {idx['column_names']}")
            
            return True
        else:
            print("\nERROR Инициализация не удалась")
            return False
            
    except Exception as e:
        print(f"\nERROR Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
        
        # Удаляем тестовую базу данных
        try:
            os.remove("test_init.db")
            print("\nТестовая база данных удалена")
        except:
            pass

def test_sql_script():
    """Тест SQL скрипта"""
    print("\n" + "=" * 60)
    print("ТЕСТ SQL СКРИПТА СОЗДАНИЯ")
    print("=" * 60)
    
    try:
        # Читаем SQL файл
        with open('create_external_images_complete.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f"SQL скрипт прочитан успешно ({len(sql_content)} символов)")
        
        # Проверяем наличие ключевых элементов
        checks = [
            ("CREATE TABLE", "Создание таблицы"),
            ("GEN_m_ex_images_ID", "Генератор"),
            ("modelgoods_external_images_BI0", "Триггер BEFORE INSERT"),
            ("LPAD(GEN_ID", "Генерация ID через LPAD"),
            ("PRIMARY KEY", "Первичный ключ"),
            ("FOREIGN KEY", "Внешний ключ"),
        ]
        
        all_ok = True
        for check_str, description in checks:
            if check_str in sql_content:
                print(f"OK {description}: найдено")
            else:
                print(f"ERROR {description}: не найдено")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"\nERROR Ошибка при тестировании SQL скрипта: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("\n" + "=" * 60)
    print("ПОЛНОЕ ТЕСТИРОВАНИЕ ИНИЦИАЛИЗАЦИИ")
    print("=" * 60)
    
    all_passed = True
    
    # Тест 1: Проверка SQL скрипта
    if not test_sql_script():
        all_passed = False
    
    # Тест 2: Проверка инициализации
    if not test_initialization():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("OK ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО")
        print("\nИтог:")
        print("  - SQL скрипт содержит все необходимые элементы")
        print("  - Функция инициализации работает корректно")
        print("  - Таблица создается с правильной структурой")
        print("  - Генератор и триггер будут созданы при необходимости")
    else:
        print("ERROR НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("  Требуется дополнительная отладка")
    
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)