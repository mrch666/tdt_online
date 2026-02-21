import sys
sys.path.append('.')
import os
import logging
import tempfile
import time
from app.database import engine
from sqlalchemy import text

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def dec64i0(modelid: str) -> str:
    """Decode first part of model ID"""
    return modelid[:8]

def dec64i1(modelid: str) -> str:
    """Decode second part of model ID"""
    return modelid[8:16]

def test_delete_problem():
    """Тест проблемы с удалением файла"""
    print("=== Тест проблемы с удалением файла ===")
    
    modelid = "000001002Qa{"
    imgext = "jpg"
    filename = f"{dec64i0(modelid)}_{dec64i1(modelid)}.{imgext}"
    img_path = os.path.join(os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases'), 
                           os.getenv('IMG_SUBDIR', 'img')) + os.sep
    
    print(f"Параметры для теста:")
    print(f"  - modelid: {modelid}")
    print(f"  - imgext: {imgext}")
    print(f"  - filename: {filename}")
    print(f"  - img_path: {img_path}")
    
    full_path = os.path.join(img_path, filename)
    
    # Создаем тестовый файл
    test_data = b'Test data for delete test'
    
    try:
        with engine.connect() as conn:
            # Шаг 1: Создаем файл
            print(f"\n--- Шаг 1: Создаем тестовый файл ---")
            try:
                # Создаем временный файл
                with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
                    tmp_file.write(test_data)
                    tmp_path = tmp_file.name
                
                # Выполняем хранимую процедуру для создания файла
                sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.' || :imgext, :file_content)""")
                
                with open(tmp_path, 'rb') as tmp_file:
                    file_blob = tmp_file.read()
                
                with conn.begin():
                    result = conn.execute(sql, {
                        'dir': img_path,
                        'modelid': modelid,
                        'imgext': imgext,
                        'file_content': file_blob
                    }).fetchall()
                
                print(f"  Файл создан, результат: {result}")
                
                # Проверяем создание файла
                time.sleep(2)
                if os.path.exists(full_path):
                    size = os.path.getsize(full_path)
                    print(f"  Файл создан: {full_path}, размер: {size} байт")
                else:
                    print(f"  ВНИМАНИЕ: Файл не создан")
                
                # Удаляем временный файл
                os.unlink(tmp_path)
                
            except Exception as e:
                print(f"  ОШИБКА при создании файла: {e}")
                import traceback
                print(f"  Трассировка: {traceback.format_exc()}")
            
            # Шаг 2: Проверяем существование файла
            print(f"\n--- Шаг 2: Проверяем существование файла ---")
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"  Файл существует: {full_path}, размер: {size} байт")
                
                # Проверяем права доступа
                try:
                    with open(full_path, 'rb') as f:
                        content = f.read(10)
                    print(f"  Права на чтение: OK, первые 10 байт: {content}")
                except Exception as e:
                    print(f"  ОШИБКА при чтении файла: {e}")
                
                # Проверяем права на удаление
                try:
                    os.unlink(full_path)
                    print(f"  Права на удаление: OK (удален напрямую)")
                    # Восстанавливаем файл для следующего теста
                    with open(full_path, 'wb') as f:
                        f.write(test_data)
                    print(f"  Файл восстановлен для следующего теста")
                except Exception as e:
                    print(f"  Права на удаление: НЕТ ({e})")
            else:
                print(f"  Файл не существует")
            
            # Шаг 3: Пробуем удалить через хранимую процедуру
            print(f"\n--- Шаг 3: Пробуем удалить через хранимую процедуру ---")
            try:
                delete_sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', '{filename}')"""
                print(f"  SQL для удаления: {delete_sql}")
                
                with conn.begin():
                    result = conn.execute(text(delete_sql)).fetchall()
                
                print(f"  Процедура выполнена, результат: {result}")
                
                # Проверяем удаление
                time.sleep(2)
                if os.path.exists(full_path):
                    size = os.path.getsize(full_path)
                    print(f"  ВНИМАНИЕ: Файл НЕ удален, размер: {size} байт")
                else:
                    print(f"  OK: Файл удален")
                    
            except Exception as e:
                print(f"  ОШИБКА при удалении через процедуру: {e}")
                import traceback
                print(f"  Трассировка: {traceback.format_exc()}")
            
            # Шаг 4: Пробуем удалить напрямую (если еще существует)
            print(f"\n--- Шаг 4: Пробуем удалить напрямую ---")
            if os.path.exists(full_path):
                try:
                    os.unlink(full_path)
                    print(f"  OK: Файл удален напрямую")
                except Exception as e:
                    print(f"  ОШИБКА при удалении напрямую: {e}")
            else:
                print(f"  Файл уже удален")
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_delete_problem()
    if success:
        print("\n=== ТЕСТ ЗАВЕРШЕН УСПЕШНО ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ ===")
        sys.exit(1)