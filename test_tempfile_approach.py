import sys
sys.path.append('.')
import os
import logging
import tempfile
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

def test_tempfile_approach():
    """Тест подхода через временный файл"""
    print("=== Тест подхода через временный файл ===")
    
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
    print(f"  - Каталог существует: {os.path.exists(img_path)}")
    
    # Создаем тестовые данные (маленький JPEG)
    test_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xf9\xff\x00\xff\xd9'
    
    try:
        with engine.connect() as conn:
            # Тест 1: Подход через временный файл (как в параметрах)
            print(f"\n1. Подход через временный файл:")
            try:
                # Создаем временный файл
                with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
                    tmp_file.write(test_data)
                    tmp_path = tmp_file.name
                
                print(f"   Временный файл создан: {tmp_path}")
                print(f"   Размер временного файла: {os.path.getsize(tmp_path)} байт")
                
                # Выполняем хранимую процедуру через временный файл
                sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.' || :imgext, :file_content)""")
                
                print(f"   SQL запрос: {sql}")
                
                with open(tmp_path, 'rb') as tmp_file:
                    file_blob = tmp_file.read()
                
                print(f"   Прочитано из временного файла: {len(file_blob)} байт")
                
                result = conn.execute(sql, {
                    'dir': img_path,
                    'modelid': modelid,
                    'imgext': imgext,
                    'file_content': file_blob
                }).fetchall()
                
                print(f"   Процедура выполнена успешно")
                print(f"   Результат: {result}")
                
                # Проверяем создание файла
                import time
                time.sleep(1)
                
                full_path = os.path.join(img_path, filename)
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    print(f"   Файл создан: {full_path}")
                    print(f"   Размер файла: {file_size} байт")
                    
                    # Проверяем содержимое файла
                    try:
                        with open(full_path, 'rb') as f:
                            saved_data = f.read()
                        print(f"   Прочитано из сохраненного файла: {len(saved_data)} байт")
                        print(f"   Первые 20 байт: {saved_data[:20]}")
                        
                        # Сравниваем данные
                        if saved_data == test_data:
                            print(f"   ✓ Данные совпадают!")
                        else:
                            print(f"   ✗ Данные не совпадают!")
                            print(f"   Размер исходных данных: {len(test_data)} байт")
                            print(f"   Размер сохраненных данных: {len(saved_data)} байт")
                            
                    except Exception as e:
                        print(f"   Ошибка при чтении файла: {e}")
                else:
                    print(f"   Файл не создан: {full_path}")
                
                # Удаляем временный файл
                try:
                    os.unlink(tmp_path)
                    print(f"   Временный файл удален")
                except Exception as e:
                    print(f"   Не удалось удалить временный файл: {e}")
                
            except Exception as e:
                print(f"   ОШИБКА при выполнении процедуры: {e}")
                import traceback
                print(f"   Трассировка: {traceback.format_exc()}")
                return False
            
            # Тест 2: Сравнение с прямым подходом
            print(f"\n2. Сравнение с прямым подходом:")
            try:
                # Прямой подход (как в текущем коде)
                sql_direct = text("""SELECT * FROM "wp_SaveBlobToFile"(:p1, :p2, :p3)""")
                
                param1 = str(img_path)
                param2 = filename
                param3 = bytes(test_data)
                
                result_direct = conn.execute(sql_direct, {
                    'p1': param1,
                    'p2': param2,
                    'p3': param3
                })
                
                print(f"   Прямой подход выполнен")
                print(f"   Результат: {result_direct}")
                
                # Пробуем получить результат
                try:
                    proc_result = result_direct.fetchone()
                    print(f"   Результат процедуры: {proc_result}")
                except Exception as fetch_error:
                    print(f"   Не удалось получить результат: {fetch_error}")
                
            except Exception as e:
                print(f"   ОШИБКА при прямом подходе: {e}")
                import traceback
                print(f"   Трассировка: {traceback.format_exc()}")
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_tempfile_approach()
    if success:
        print("\n=== ТЕСТ ЗАВЕРШЕН УСПЕШНО ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ ===")
        sys.exit(1)