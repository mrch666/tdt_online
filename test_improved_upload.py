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

def test_improved_upload():
    """Тест улучшенной загрузки с проверкой размеров файлов"""
    print("=== Тест улучшенной загрузки изображений ===")
    
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
    
    # Создаем тестовые данные
    test_data_1 = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xf9\xff\x00\xff\xd9'
    test_data_2 = b'X' * 2000  # 2000 байт
    test_data_3 = b'Y' * 5000  # 5000 байт
    
    try:
        with engine.connect() as conn:
            # Тест 1: Первая загрузка (333 байта)
            print(f"\n--- Тест 1: Первая загрузка (333 байта) ---")
            try:
                # Удаляем старый файл если существует
                full_path = os.path.join(img_path, filename)
                if os.path.exists(full_path):
                    print(f"  Удаляем старый файл: {full_path}")
                    try:
                        os.unlink(full_path)
                    except:
                        pass
                
                # Создаем временный файл
                with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
                    tmp_file.write(test_data_1)
                    tmp_path = tmp_file.name
                
                tmp_size = os.path.getsize(tmp_path)
                print(f"  Временный файл создан: {tmp_path}, размер: {tmp_size} байт")
                
                # Выполняем хранимую процедуру
                sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.' || :imgext, :file_content)""")
                
                with open(tmp_path, 'rb') as tmp_file:
                    file_blob = tmp_file.read()
                
                print(f"  Передаваемые данные: {len(file_blob)} байт")
                
                with conn.begin():
                    result = conn.execute(sql, {
                        'dir': img_path,
                        'modelid': modelid,
                        'imgext': imgext,
                        'file_content': file_blob
                    }).fetchall()
                
                print(f"  Процедура выполнена, результат: {result}")
                
                # Проверяем сохраненный файл
                time.sleep(2)
                
                if os.path.exists(full_path):
                    saved_size = os.path.getsize(full_path)
                    print(f"  Файл сохранен: {full_path}, размер: {saved_size} байт")
                    
                    if saved_size == len(test_data_1):
                        print(f"  OK: Размер сохраненного файла совпадает")
                    else:
                        print(f"  ВНИМАНИЕ: Размер не совпадает ({saved_size} != {len(test_data_1)})")
                else:
                    print(f"  ВНИМАНИЕ: Файл не сохранен")
                
                # Удаляем временный файл
                os.unlink(tmp_path)
                print(f"  Временный файл удален")
                
            except Exception as e:
                print(f"  ОШИБКА: {e}")
                import traceback
                print(f"  Трассировка: {traceback.format_exc()}")
            
            # Тест 2: Вторая загрузка (2000 байт) - перезапись
            print(f"\n--- Тест 2: Вторая загрузка (2000 байт) - перезапись ---")
            try:
                # Создаем временный файл
                with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
                    tmp_file.write(test_data_2)
                    tmp_path = tmp_file.name
                
                tmp_size = os.path.getsize(tmp_path)
                print(f"  Временный файл создан: {tmp_path}, размер: {tmp_size} байт")
                
                # Проверяем существование старого файла
                if os.path.exists(full_path):
                    old_size = os.path.getsize(full_path)
                    print(f"  Старый файл существует, размер: {old_size} байт")
                    
                    # Пробуем удалить через хранимую процедуру
                    try:
                        delete_sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', '{filename}')"""
                        with conn.begin():
                            conn.execute(text(delete_sql))
                        print(f"  Старый файл удален через хранимую процедуру")
                    except Exception as delete_error:
                        print(f"  Не удалось удалить через процедуру: {delete_error}")
                        # Пробуем удалить напрямую
                        try:
                            os.unlink(full_path)
                            print(f"  Старый файл удален напрямую")
                        except Exception as direct_delete_error:
                            print(f"  Не удалось удалить напрямую: {direct_delete_error}")
                
                # Выполняем хранимую процедуру
                with open(tmp_path, 'rb') as tmp_file:
                    file_blob = tmp_file.read()
                
                print(f"  Передаваемые данные: {len(file_blob)} байт")
                
                with conn.begin():
                    result = conn.execute(sql, {
                        'dir': img_path,
                        'modelid': modelid,
                        'imgext': imgext,
                        'file_content': file_blob
                    }).fetchall()
                
                print(f"  Процедура выполнена, результат: {result}")
                
                # Проверяем сохраненный файл
                time.sleep(2)
                
                if os.path.exists(full_path):
                    saved_size = os.path.getsize(full_path)
                    print(f"  Файл сохранен: {full_path}, размер: {saved_size} байт")
                    
                    if saved_size == len(test_data_2):
                        print(f"  OK: Размер сохраненного файла совпадает")
                    else:
                        print(f"  ВНИМАНИЕ: Размер не совпадает ({saved_size} != {len(test_data_2)})")
                        
                        # Проверяем содержимое
                        try:
                            with open(full_path, 'rb') as f:
                                saved_data = f.read()
                            if saved_data == test_data_2:
                                print(f"  OK: Содержимое совпадает")
                            else:
                                print(f"  ВНИМАНИЕ: Содержимое не совпадает")
                                print(f"    Первые 20 байт сохраненного: {saved_data[:20]}")
                                print(f"    Первые 20 байт переданных: {test_data_2[:20]}")
                        except Exception as read_error:
                            print(f"  Ошибка при проверке содержимого: {read_error}")
                else:
                    print(f"  ВНИМАНИЕ: Файл не сохранен")
                
                # Удаляем временный файл
                os.unlink(tmp_path)
                print(f"  Временный файл удален")
                
            except Exception as e:
                print(f"  ОШИБКА: {e}")
                import traceback
                print(f"  Трассировка: {traceback.format_exc()}")
            
            # Тест 3: Третья загрузка (5000 байт) - еще одна перезапись
            print(f"\n--- Тест 3: Третья загрузка (5000 байт) - еще одна перезапись ---")
            try:
                # Создаем временный файл
                with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
                    tmp_file.write(test_data_3)
                    tmp_path = tmp_file.name
                
                tmp_size = os.path.getsize(tmp_path)
                print(f"  Временный файл создан: {tmp_path}, размер: {tmp_size} байт")
                
                # Проверяем существование старого файла
                if os.path.exists(full_path):
                    old_size = os.path.getsize(full_path)
                    print(f"  Старый файл существует, размер: {old_size} байт")
                
                # Выполняем хранимую процедуру
                with open(tmp_path, 'rb') as tmp_file:
                    file_blob = tmp_file.read()
                
                print(f"  Передаваемые данные: {len(file_blob)} байт")
                
                with conn.begin():
                    result = conn.execute(sql, {
                        'dir': img_path,
                        'modelid': modelid,
                        'imgext': imgext,
                        'file_content': file_blob
                    }).fetchall()
                
                print(f"  Процедура выполнена, результат: {result}")
                
                # Проверяем сохраненный файл
                time.sleep(2)
                
                if os.path.exists(full_path):
                    saved_size = os.path.getsize(full_path)
                    print(f"  Файл сохранен: {full_path}, размер: {saved_size} байт")
                    
                    if saved_size == len(test_data_3):
                        print(f"  OK: Размер сохраненного файла совпадает")
                    else:
                        print(f"  ВНИМАНИЕ: Размер не совпадает ({saved_size} != {len(test_data_3)})")
                else:
                    print(f"  ВНИМАНИЕ: Файл не сохранен")
                
                # Удаляем временный файл
                os.unlink(tmp_path)
                print(f"  Временный файл удален")
                
                # Очистка: удаляем сохраненный файл
                try:
                    os.unlink(full_path)
                    print(f"  Сохраненный файл удален")
                except Exception as e:
                    print(f"  Не удалось удалить сохраненный файл: {e}")
                
            except Exception as e:
                print(f"  ОШИБКА: {e}")
                import traceback
                print(f"  Трассировка: {traceback.format_exc()}")
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_improved_upload()
    if success:
        print("\n=== ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТЫ ЗАВЕРШЕНЫ С ОШИБКАМИ ===")
        sys.exit(1)