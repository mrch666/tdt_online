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

def test_param_length():
    """Тест проверки ограничения длины параметра"""
    print("=== ТЕСТ ОГРАНИЧЕНИЯ ДЛИНЫ ПАРАМЕТРА ===")
    
    modelid = "000001002Qa{"
    imgext = "jpg"
    filename = f"{dec64i0(modelid)}_{dec64i1(modelid)}.{imgext}"
    img_path = os.path.join(os.getenv('BASE_DIR', 'C:\\tdt3\\bases'), 
                           os.getenv('IMG_SUBDIR', 'img')) + os.sep
    
    print(f"Параметры:")
    print(f"  - modelid: {modelid}")
    print(f"  - imgext: {imgext}")
    print(f"  - filename: {filename}")
    print(f"  - img_path: {img_path}")
    
    # Тестируем разные размеры данных
    test_cases = [
        ("12 байт (ожидаемый размер)", b'A' * 12),
        ("13 байт (на 1 больше)", b'B' * 13),
        ("16 байт", b'C' * 16),
        ("17 байт (как в ошибке)", b'D' * 17),
        ("100 байт", b'E' * 100),
        ("1000 байт", b'F' * 1000),
    ]
    
    try:
        with engine.connect() as conn:
            for test_name, test_data in test_cases:
                print(f"\n--- {test_name} ---")
                
                try:
                    # Создаем временный файл
                    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
                        tmp_file.write(test_data)
                        tmp_path = tmp_file.name
                    
                    print(f"  Размер данных: {len(test_data)} байт")
                    
                    # Выполняем хранимую процедуру
                    sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.' || :imgext, :file_content)""")
                    
                    with open(tmp_path, 'rb') as tmp_file:
                        file_blob = tmp_file.read()
                    
                    print(f"  Передаем: {len(file_blob)} байт")
                    
                    with conn.begin():
                        result = conn.execute(sql, {
                            'dir': img_path,
                            'modelid': modelid,
                            'imgext': imgext,
                            'file_content': file_blob
                        }).fetchall()
                    
                    print(f"  УСПЕХ: Процедура выполнена: {result}")
                    
                    # Проверяем файл
                    full_path = os.path.join(img_path, filename)
                    time.sleep(1)
                    if os.path.exists(full_path):
                        saved_size = os.path.getsize(full_path)
                        print(f"  Файл сохранен: {saved_size} байт")
                        
                        if saved_size == len(test_data):
                            print(f"  OK: Размер совпадает")
                        else:
                            print(f"  WARNING: Размер не совпадает")
                    else:
                        print(f"  WARNING: Файл не создан")
                    
                    # Удаляем временный файл
                    os.unlink(tmp_path)
                    
                    # Удаляем созданный файл через процедуру
                    try:
                        delete_sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', '{filename}')"""
                        with conn.begin():
                            conn.execute(text(delete_sql))
                        print(f"  Файл удален")
                        time.sleep(1)
                    except Exception as delete_error:
                        print(f"  Не удалось удалить файл: {delete_error}")
                    
                except Exception as e:
                    print(f"  ОШИБКА: {e}")
                    if "too long" in str(e):
                        print(f"  ПРИЧИНА: Превышено ограничение длины параметра")
                    
                    # Удаляем временный файл если он создан
                    if 'tmp_path' in locals():
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_param_length()
    if success:
        print("\n=== ТЕСТ ЗАВЕРШЕН ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ ===")
        sys.exit(1)