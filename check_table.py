from app.database import SessionLocal
from app.database_utils import check_table_exists, get_table_info

def main():
    db = SessionLocal()
    try:
        # Проверяем существование таблицы
        table_name = "modelgoods_external_images"
        exists = check_table_exists(db, table_name)
        print(f"Таблица {table_name} существует: {exists}")
        
        if exists:
            # Получаем информацию о таблице
            info = get_table_info(db, table_name)
            print(f"\nИнформация о таблице {table_name}:")
            print(f"Колонки: {len(info.get('columns', []))}")
            for col in info.get('columns', []):
                print(f"  - {col['name']}: {col['type']} {'(PK)' if col['primary_key'] else ''}")
            
            print(f"\nИндексы: {len(info.get('indexes', []))}")
            for idx in info.get('indexes', []):
                print(f"  - {idx['name']}: {idx['columns']}")
            
            print(f"\nВнешние ключи: {len(info.get('foreign_keys', []))}")
            for fk in info.get('foreign_keys', []):
                print(f"  - {fk['name']}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        else:
            print("Таблица не существует. Нужно создать её вручную.")
            
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()