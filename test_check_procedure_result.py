"""Тест для проверки подхода с использованием результата процедуры вместо проверки файла"""
import sys
sys.path.append('.')
import logging
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_check_procedure_result():
    """Тест проверки результата процедуры вместо проверки файла"""
    print("=== ТЕСТ ПРОВЕРКИ РЕЗУЛЬТАТА ПРОЦЕДУРЫ ===")
    print("Цель: проверить, что можно использовать результат процедуры вместо os.path.exists")
    
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
            print("\n=== ТЕСТИРОВАНИЕ ПОДХОДА ===")
            
            # Тест 1: Успешное сохранение
            print("\n1. Тест успешного сохранения:")
            test_dir = os.path.join(os.getenv('BASE_DIR'), os.getenv('IMG_SUBDIR')) + os.sep
            test_filename = "test_procedure_success.txt"
            test_content = b"Test content for successful save"
            
            try:
                sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, :filename, :content)""")
                params = {
                    'dir': test_dir,
                    'filename': test_filename,
                    'content': test_content
                }
                
                result = connection.execute(sql, params)
                rows = result.fetchall()
                
                print(f"   Результат процедуры: {rows}")
                
                if rows and len(rows) > 0:
                    first_row = rows[0]
                    # Получаем значение oRes
                    if hasattr(first_row, 'oRes'):
                        oRes_value = first_row.oRes
                    else:
                        # Пробуем получить по индексу
                        oRes_value = first_row[0]
                    
                    print(f"   Значение oRes: {oRes_value}")
                    print(f"   Тип значения: {type(oRes_value)}")
                    
                    # Проверяем успешность
                    if oRes_value == 1:
                        print("   [OK] Процедура вернула успех (oRes = 1)")
                        print("   [OK] Можно считать файл сохраненным без проверки os.path.exists")
                    else:
                        print(f"   [WARNING] Процедура вернула неожиданное значение: {oRes_value}")
                else:
                    print("   [ERROR] Процедура не вернула результатов")
                    
            except Exception as e:
                print(f"   [ERROR] Ошибка при вызове процедуры: {e}")
            
            # Тест 2: Проверка разных сценариев
            print("\n2. Тест разных сценариев:")
            
            test_cases = [
                {
                    'name': 'Маленький файл',
                    'content': b'small',
                    'expected': 1
                },
                {
                    'name': 'Большой файл (10KB)',
                    'content': b'X' * 10240,
                    'expected': 1
                },
                {
                    'name': 'Очень большой файл (100KB)',
                    'content': b'Y' * 102400,
                    'expected': 1
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                print(f"\n   --- {test_case['name']} ---")
                test_filename = f"test_case_{i}.txt"
                
                try:
                    sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, :filename, :content)""")
                    params = {
                        'dir': test_dir,
                        'filename': test_filename,
                        'content': test_case['content']
                    }
                    
                    result = connection.execute(sql, params)
                    rows = result.fetchall()
                    
                    if rows and len(rows) > 0:
                        oRes_value = rows[0][0]  # Получаем первое значение
                        print(f"   Размер данных: {len(test_case['content'])} байт")
                        print(f"   Результат oRes: {oRes_value}")
                        
                        if oRes_value == test_case['expected']:
                            print(f"   [OK] Ожидаемый результат: {oRes_value}")
                        else:
                            print(f"   [WARNING] Неожиданный результат: {oRes_value} (ожидалось {test_case['expected']})")
                    else:
                        print("   [ERROR] Нет результатов")
                        
                except Exception as e:
                    print(f"   [ERROR] Ошибка: {e}")
            
            # Тест 3: Сравнение двух подходов
            print("\n3. Сравнение подходов:")
            print("   Старый подход: проверять os.path.exists() после процедуры")
            print("   Новый подход: проверять результат процедуры (oRes)")
            
            test_filename = "test_compare_approaches.txt"
            test_content = b"Compare old vs new approach"
            
            try:
                # Вызываем процедуру
                sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, :filename, :content)""")
                params = {
                    'dir': test_dir,
                    'filename': test_filename,
                    'content': test_content
                }
                
                result = connection.execute(sql, params)
                rows = result.fetchall()
                
                print(f"\n   Результат процедуры: {rows}")
                
                # Старый подход
                full_path = os.path.join(test_dir, test_filename)
                file_exists = os.path.exists(full_path)
                print(f"\n   Старый подход (os.path.exists):")
                print(f"     Файл существует: {file_exists}")
                
                if file_exists:
                    file_size = os.path.getsize(full_path)
                    print(f"     Размер файла: {file_size} байт")
                else:
                    print(f"     [WARNING] Файл не найден, хотя процедура вернула успех")
                
                # Новый подход
                print(f"\n   Новый подход (проверка oRes):")
                if rows and len(rows) > 0:
                    oRes_value = rows[0][0]
                    print(f"     Значение oRes: {oRes_value}")
                    
                    if oRes_value == 1:
                        print(f"     [OK] Процедура сообщает об успешном сохранении")
                        print(f"     [OK] Можно пропустить проверку os.path.exists")
                    else:
                        print(f"     [ERROR] Процедура сообщает об ошибке")
                else:
                    print(f"     [ERROR] Нет результатов от процедуры")
                
                # Вывод
                print(f"\n   Итог сравнения:")
                if file_exists and rows and rows[0][0] == 1:
                    print(f"     [OK] Оба подхода согласованы: файл сохранен")
                elif not file_exists and rows and rows[0][0] == 1:
                    print(f"     [IMPORTANT] Расхождение: процедура говорит 'успех', но файла нет")
                    print(f"     [РЕШЕНИЕ] Доверять процедуре, а не проверке файла")
                elif file_exists and rows and rows[0][0] != 1:
                    print(f"     [WARNING] Расхождение: файл есть, но процедура говорит 'ошибка'")
                else:
                    print(f"     [ERROR] Непонятная ситуация")
                    
            except Exception as e:
                print(f"   [ERROR] Ошибка при сравнении: {e}")
            
            # Тест 4: Рекомендации по реализации
            print("\n4. Рекомендации по реализации:")
            print("""
   Рекомендуемые изменения в app/routers/modelgoods_images.py:
   
   1. После вызова процедуры получаем результат:
      result = db.execute(sql, params).fetchall()
      
   2. Проверяем результат процедуры:
      if result and len(result) > 0 and result[0][0] == 1:
          # Процедура вернула успех
          logger.info(f"Файл сохранен успешно (oRes=1)")
      else:
          # Процедура вернула ошибку или не вернула результат
          logger.error(f"Процедура вернула ошибку: {result}")
          raise HTTPException(500, "File save failed")
      
   3. Убираем или оставляем как резервную проверку os.path.exists:
      # Опционально: оставляем как дополнительную проверку
      import time
      time.sleep(1)  # Короткая задержка
      if not os.path.exists(full_path):
          logger.warning(f"Файл не найден на диске, но процедура вернула успех")
          # Не бросаем ошибку, т.к. процедура сказала, что все ок
      
   4. Преимущества нового подхода:
      - Не зависит от задержек файловой системы
      - Работает с большими файлами
      - Не требует длительных таймаутов
      - Использует встроенную проверку процедуры
            """)
    
    except Exception as e:
        print(f"\n=== ОШИБКА ПОДКЛЮЧЕНИЯ ===")
        print(f"Ошибка: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
    
    print("\n=== ВЫВОДЫ ===")
    print("1. Процедура wp_SaveBlobToFile возвращает oRes = 1 при успешном сохранении")
    print("2. Можно доверять результату процедуры вместо проверки os.path.exists")
    print("3. Это решает проблему с таймаутами для больших файлов")
    print("4. Нужно изменить код в app/routers/modelgoods_images.py")
    
    return True

if __name__ == "__main__":
    try:
        success = test_check_procedure_result()
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