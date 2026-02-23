"""Тест для изучения возвращаемого значения хранимой процедуры wp_SaveBlobToFile"""
import sys
sys.path.append('.')
import logging
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_procedure_return_value():
    """Тест для изучения возвращаемого значения процедуры"""
    print("=== ТЕСТ ВОЗВРАЩАЕМОГО ЗНАЧЕНИЯ ПРОЦЕДУРЫ ===")
    print("Цель: узнать, что возвращает wp_SaveBlobToFile при успешном сохранении")
    
    # Загружаем переменные окружения
    load_dotenv()
    
    # Подключаемся к базе данных
    SQLALCHEMY_DATABASE_URL = (
        f"firebird+fdb://"
        f"{os.getenv('FIREBIRD_USER', 'SYSDBA')}:{os.getenv('FIREBIRD_PASSWORD', 'masterkey')}@"
        f"{os.getenv('FIREBIRD_HOST', 'localhost')}:{os.getenv('FIREBIRD_PORT', 3055)}/"
        f"{os.getenv('BASE_DIR')}/{os.getenv('DATABASE_NAME')}"
    )
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={
            "fb_library_name": os.getenv('FBCLIENT_PATH', 'C:\\Program Files (x86)\\tdt3\\fbclient.dll'),
            "charset": "WIN1251"
        }
    )
    
    try:
        with engine.connect() as connection:
            print("\n=== ИЗУЧЕНИЕ ПРОЦЕДУРЫ ===")
            
            # 1. Попробуем получить описание процедуры
            print("\n1. Получение информации о процедуре:")
            try:
                result = connection.execute(text("""
                    SELECT RDB$PROCEDURE_NAME, RDB$PROCEDURE_SOURCE
                    FROM RDB$PROCEDURES
                    WHERE RDB$PROCEDURE_NAME = 'WP_SAVEBLOBTOFILE'
                """))
                
                for row in result:
                    print(f"   Имя процедуры: {row[0]}")
                    print(f"   Исходный код: {row[1][:200] if row[1] else 'Нет исходного кода'}")
            except Exception as e:
                print(f"   [ERROR] Не удалось получить информацию о процедуре: {e}")
            
            # 2. Попробуем получить параметры процедуры
            print("\n2. Получение параметров процедуры:")
            try:
                result = connection.execute(text("""
                    SELECT 
                        RDB$PARAMETER_NAME,
                        RDB$PARAMETER_TYPE,
                        RDB$FIELD_SOURCE,
                        RDB$DESCRIPTION
                    FROM RDB$PROCEDURE_PARAMETERS
                    WHERE RDB$PROCEDURE_NAME = 'WP_SAVEBLOBTOFILE'
                    ORDER BY RDB$PARAMETER_NUMBER
                """))
                
                params = []
                for row in result:
                    param_name = row[0].strip()
                    param_type = "INPUT" if row[1] == 0 else "OUTPUT"
                    param_source = row[2].strip() if row[2] else "UNKNOWN"
                    param_desc = row[3].strip() if row[3] else ""
                    
                    params.append({
                        'name': param_name,
                        'type': param_type,
                        'source': param_source,
                        'description': param_desc
                    })
                    
                    print(f"   Параметр: {param_name}")
                    print(f"     Тип: {param_type}")
                    print(f"     Источник: {param_source}")
                    print(f"     Описание: {param_desc}")
                
                print(f"   Всего параметров: {len(params)}")
                
            except Exception as e:
                print(f"   [ERROR] Не удалось получить параметры процедуры: {e}")
            
            # 3. Тестируем вызов процедуры с тестовыми данными
            print("\n3. Тестовый вызов процедуры:")
            
            # Создаем тестовые данные
            test_dir = os.path.join(os.getenv('BASE_DIR'), os.getenv('IMG_SUBDIR')) + os.sep
            test_filename = "test_procedure_return.txt"
            test_content = b"Test content for procedure return value check"
            
            try:
                # Вызываем процедуру
                sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, :filename, :content)""")
                
                params = {
                    'dir': test_dir,
                    'filename': test_filename,
                    'content': test_content
                }
                
                print(f"   Вызываем процедуру с параметрами:")
                print(f"     dir: {test_dir}")
                print(f"     filename: {test_filename}")
                print(f"     content size: {len(test_content)} байт")
                
                result = connection.execute(sql, params)
                
                # Получаем все строки результата
                rows = result.fetchall()
                
                print(f"\n   Результат процедуры:")
                print(f"     Количество строк: {len(rows)}")
                
                for i, row in enumerate(rows):
                    print(f"     Строка {i+1}: {row}")
                    print(f"     Тип строки: {type(row)}")
                    
                    # Пробуем разобрать результат
                    if hasattr(row, '_asdict'):
                        row_dict = row._asdict()
                        print(f"     Как словарь: {row_dict}")
                    
                    # Пробуем получить по индексу
                    for j, value in enumerate(row):
                        print(f"       Колонка {j}: {value} (тип: {type(value)})")
                
                # 4. Проверяем, был ли создан файл
                print("\n4. Проверка созданного файла:")
                full_path = os.path.join(test_dir, test_filename)
                
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    print(f"   Файл создан: {full_path}")
                    print(f"   Размер файла: {file_size} байт")
                    
                    # Удаляем тестовый файл
                    try:
                        os.remove(full_path)
                        print("   Тестовый файл удален")
                    except Exception as e:
                        print(f"   [WARNING] Не удалось удалить тестовый файл: {e}")
                else:
                    print(f"   [WARNING] Файл не создан: {full_path}")
                
                # 5. Анализируем результат
                print("\n5. Анализ результата:")
                if rows:
                    first_row = rows[0]
                    if len(first_row) == 1:
                        print(f"   Процедура возвращает одно значение: {first_row[0]}")
                        print(f"   Тип значения: {type(first_row[0])}")
                        
                        # Проверяем, является ли результат числом (кодом ошибки/успеха)
                        if isinstance(first_row[0], (int, float)):
                            print(f"   Числовое значение: {first_row[0]}")
                            if first_row[0] == 0 or first_row[0] == 1:
                                print(f"   Вероятно, код успеха: {first_row[0]}")
                            else:
                                print(f"   Возможно, код ошибки: {first_row[0]}")
                        elif isinstance(first_row[0], str):
                            print(f"   Строковое значение: '{first_row[0]}'")
                            if first_row[0].lower() in ['success', 'ok', 'true', '1']:
                                print(f"   Вероятно, признак успеха")
                            elif first_row[0].lower() in ['error', 'fail', 'false', '0']:
                                print(f"   Вероятно, признак ошибки")
                    else:
                        print(f"   Процедура возвращает {len(first_row)} значений")
                        for i, value in enumerate(first_row):
                            print(f"     Значение {i+1}: {value} (тип: {type(value)})")
                else:
                    print("   Процедура не вернула результатов (пустой результат)")
                
            except Exception as e:
                print(f"   [ERROR] Ошибка при вызове процедуры: {e}")
                import traceback
                print(f"   Трассировка: {traceback.format_exc()}")
            
            # 6. Проверяем другие возможные процедуры
            print("\n6. Поиск похожих процедур:")
            try:
                result = connection.execute(text("""
                    SELECT RDB$PROCEDURE_NAME
                    FROM RDB$PROCEDURES
                    WHERE RDB$PROCEDURE_NAME LIKE '%SAVE%'
                       OR RDB$PROCEDURE_NAME LIKE '%BLOB%'
                       OR RDB$PROCEDURE_NAME LIKE '%FILE%'
                    ORDER BY RDB$PROCEDURE_NAME
                """))
                
                procedures = []
                for row in result:
                    proc_name = row[0].strip()
                    procedures.append(proc_name)
                
                print(f"   Найдено процедур: {len(procedures)}")
                for proc in procedures[:10]:  # Показываем первые 10
                    print(f"     - {proc}")
                
                if len(procedures) > 10:
                    print(f"     ... и еще {len(procedures) - 10} процедур")
                    
            except Exception as e:
                print(f"   [ERROR] Не удалось найти процедуры: {e}")
    
    except Exception as e:
        print(f"\n=== ОШИБКА ПОДКЛЮЧЕНИЯ ===")
        print(f"Ошибка: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
    
    print("\n=== ВЫВОДЫ ===")
    print("1. Нужно определить, что именно возвращает wp_SaveBlobToFile")
    print("2. Если процедура возвращает признак успеха, можно использовать его")
    print("3. Если нет - нужно искать альтернативные способы проверки")
    print("4. Возможно, процедура возвращает код ошибки/успеха (0/1)")
    
    return True

if __name__ == "__main__":
    try:
        success = test_procedure_return_value()
        if success:
            print("\n=== ТЕСТ ЗАВЕРШЕН ===")
            sys.exit(0)
    except Exception as e:
        print(f"\n=== НЕОЖИДАННАЯ ОШИБКА ===")
        print(f"Ошибка: {e}")
        sys.exit(1)