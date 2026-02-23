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

def test_check_file():
    """Тест проверки файла после выполнения процедуры"""
    print("=== ТЕСТ ПРОВЕРКИ ФАЙЛА ПОСЛЕ ПРОЦЕДУРЫ ===")
    
    modelid = "000001002Qa{"
    imgext = "jpg"
    filename = f"{dec64i0(modelid)}_{dec64i1(modelid)}.{imgext}"
    img_path = os.path.join(os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases'), 
                           os.getenv('IMG_SUBDIR', 'img')) + os.sep
    
    print(f"Параметры:")
    print(f"  - modelid: {modelid}")
    print(f"  - imgext: {imgext}")
    print(f"  - filename: {filename}")
    print(f"  - img_path: {img_path}")
    
    full_path = os.path.join(img_path, filename)
    
    # Тестовые данные
    test_data = b'Simple test data'
    
    try:
        with engine.connect() as conn:
            # Шаг 1: Очищаем старый файл
            print(f"\n--- Шаг 1: Очищаем старый файл ---")
            if os.path.exists(full_path):
                print(f"  Старый файл существует, удаляем...")
                try:
                    delete_sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', '{filename}')"""
                    with conn.begin():
                        result = conn.execute(text(delete_sql)).fetchall()
                    print(f"  Процедура удаления выполнена: {result}")
                    time.sleep(2)
                except Exception as e:
                    print(f"  Ошибка при удалении: {e}")
            
            # Шаг 2: Проверяем, что файла нет
            print(f"\n--- Шаг 2: Проверяем отсутствие файла ---")
            if os.path.exists(full_path):
                print(f"  ВНИМАНИЕ: Файл все еще существует: {full_path}")
                size = os.path.getsize(full_path)
                print(f"  Размер: {size} байт")
            else:
                print(f"  OK: Файл не существует")
            
            # Шаг 3: Создаем временный файл
            print(f"\n--- Шаг 3: Создаем временный файл ---")
            with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
                tmp_file.write(test_data)
                tmp_path = tmp_file.name
            
            print(f"  Временный файл: {tmp_path}, размер: {os.path.getsize(tmp_path)} байт")
            
            # Шаг 4: Выполняем процедуру сохранения
            print(f"\n--- Шаг 4: Выполняем процедуру сохранения ---")
            sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.' || :imgext, :file_content)""")
            
            with open(tmp_path, 'rb') as tmp_file:
                file_blob = tmp_file.read()
            
            print(f"  Передаваемые данные: {len(file_blob)} байт")
            
            try:
                with conn.begin():
                    result = conn.execute(sql, {
                        'dir': img_path,
                        'modelid': modelid,
                        'imgext': imgext,
                        'file_content': file_blob
                    }).fetchall()
                
                print(f"  Процедура выполнена успешно: {result}")
            except Exception as e:
                print(f"  ОШИБКА при выполнении процедуры: {e}")
                import traceback
                print(f"  Трассировка: {traceback.format_exc()}")
            
            # Шаг 5: Проверяем файл сразу после процедуры
            print(f"\n--- Шаг 5: Проверяем файл сразу после процедуры ---")
            time.sleep(1)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"  Файл создан: {full_path}, размер: {size} байт")
                
                # Проверяем содержимое
                with open(full_path, 'rb') as f:
                    saved_data = f.read()
                print(f"  Содержимое файла: {saved_data}")
                
                if saved_data == test_data:
                    print(f"  OK: Содержимое совпадает")
                else:
                    print(f"  ERROR: Содержимое не совпадает")
            else:
                print(f"  ERROR: Файл не создан")
                
                # Проверяем права доступа к каталогу
                print(f"\n--- Проверка прав доступа к каталогу ---")
                if os.path.exists(img_path):
                    print(f"  Каталог существует: {img_path}")
                    
                    # Пробуем создать тестовый файл напрямую
                    test_file = os.path.join(img_path, "test_direct.txt")
                    try:
                        with open(test_file, 'w') as f:
                            f.write("Test direct write")
                        print(f"  OK: Можем создавать файлы в каталоге")
                        os.unlink(test_file)
                        print(f"  Тестовый файл удален")
                    except Exception as e:
                        print(f"  ERROR: Не можем создавать файлы в каталоге: {e}")
                else:
                    print(f"  ERROR: Каталог не существует: {img_path}")
            
            # Шаг 6: Очистка
            print(f"\n--- Шаг 6: Очистка ---")
            os.unlink(tmp_path)
            print(f"  Временный файл удален")
            
            if os.path.exists(full_path):
                try:
                    delete_sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', '{filename}')"""
                    with conn.begin():
                        conn.execute(text(delete_sql))
                    print(f"  Созданный файл удален через процедуру")
                    time.sleep(1)
                except Exception as e:
                    print(f"  Не удалось удалить файл: {e}")
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_check_file()
    if success:
        print("\n=== ТЕСТ ЗАВЕРШЕН ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ ===")
        sys.exit(1)