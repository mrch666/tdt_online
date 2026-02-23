import sys
sys.path.append('.')
import os
import logging
from app.database import engine
from sqlalchemy import text

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def check_proc_definition():
    """Проверка определения хранимой процедуры"""
    print("=== ПРОВЕРКА ОПРЕДЕЛЕНИЯ ХРАНИМОЙ ПРОЦЕДУРЫ ===")
    
    try:
        with engine.connect() as conn:
            # Пробуем получить определение процедуры
            print("\n--- Пробуем получить определение процедуры wp_SaveBlobToFile ---")
            
            # В Firebird можно попробовать получить информацию о процедуре
            try:
                # Пробуем разные запросы для получения информации о процедуре
                queries = [
                    """SELECT RDB$PROCEDURE_NAME, RDB$PROCEDURE_SOURCE 
                       FROM RDB$PROCEDURES 
                       WHERE RDB$PROCEDURE_NAME = 'WP_SAVEBLOBTOFILE'""",
                    """SELECT RDB$PARAMETER_NAME, RDB$PARAMETER_TYPE, RDB$FIELD_SOURCE, RDB$PARAMETER_NUMBER
                       FROM RDB$PROCEDURE_PARAMETERS 
                       WHERE RDB$PROCEDURE_NAME = 'WP_SAVEBLOBTOFILE'
                       ORDER BY RDB$PARAMETER_NUMBER""",
                    """SELECT RDB$PARAMETER_NAME, RDB$FIELD_TYPE, RDB$FIELD_LENGTH, RDB$FIELD_SCALE
                       FROM RDB$PROCEDURE_PARAMETERS P
                       JOIN RDB$FIELDS F ON P.RDB$FIELD_SOURCE = F.RDB$FIELD_NAME
                       WHERE P.RDB$PROCEDURE_NAME = 'WP_SAVEBLOBTOFILE'
                       ORDER BY P.RDB$PARAMETER_NUMBER"""
                ]
                
                for i, query in enumerate(queries):
                    print(f"\nЗапрос {i+1}:")
                    print(f"SQL: {query}")
                    try:
                        result = conn.execute(text(query)).fetchall()
                        if result:
                            print(f"Результат: {result}")
                            for row in result:
                                print(f"  {row}")
                        else:
                            print("  Нет результатов")
                    except Exception as e:
                        print(f"  Ошибка: {e}")
                
                # Пробуем вызвать процедуру с минимальными данными
                print("\n--- Пробуем вызвать процедуру с разными типами данных ---")
                
                test_cases = [
                    ("Пустая строка", b''),
                    ("1 байт", b'A'),
                    ("11 байт", b'A' * 11),
                    ("12 байт", b'A' * 12),
                    ("13 байт", b'A' * 13),
                ]
                
                for test_name, test_data in test_cases:
                    print(f"\nТест: {test_name} ({len(test_data)} байт)")
                    try:
                        sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, :filename, :file_content)""")
                        
                        result = conn.execute(sql, {
                            'dir': 'C:\\test',
                            'filename': 'test.txt',
                            'file_content': test_data
                        }).fetchall()
                        
                        print(f"  УСПЕХ: {result}")
                    except Exception as e:
                        print(f"  ОШИБКА: {e}")
                        if "too long" in str(e):
                            # Пробуем извлечь информацию об ожидаемой длине
                            import re
                            match = re.search(r'expected (\d+), found (\d+)', str(e))
                            if match:
                                expected = match.group(1)
                                found = match.group(2)
                                print(f"  Ожидалось: {expected} байт, передано: {found} байт")
                
            except Exception as e:
                print(f"Ошибка при проверке процедуры: {e}")
                import traceback
                print(f"Трассировка: {traceback.format_exc()}")
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = check_proc_definition()
    if success:
        print("\n=== ПРОВЕРКА ЗАВЕРШЕНА ===")
        sys.exit(0)
    else:
        print("\n=== ПРОВЕРКА ЗАВЕРШЕНА С ОШИБКАМИ ===")
        sys.exit(1)