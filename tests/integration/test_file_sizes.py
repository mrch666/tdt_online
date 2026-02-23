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

def test_file_sizes():
    """Тест проверки размеров файлов при загрузке изображений"""
    print("=== Тест проверки размеров файлов ===")
    
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
    
    # Создаем тестовые данные разного размера
    test_cases = [
        ("Маленький файл (333 байта)", b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xf9\xff\x00\xff\xd9'),
        ("Средний файл (1000 байт)", b'X' * 1000),
        ("Большой файл (10000 байт)", b'Y' * 10000),
    ]
    
    try:
        with engine.connect() as conn:
            for test_name, test_data in test_cases:
                print(f"\n--- Тест: {test_name} ---")
                print(f"  Исходный размер данных: {len(test_data)} байт")
                
                # Тест 1: Проверка временного файла
                print(f"  1. Создание временного файла:")
                try:
                    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
                        tmp_file.write(test_data)
                        tmp_path = tmp_file.name
                    
                    tmp_size = os.path.getsize(tmp_path)
                    print(f"     Временный файл создан: {tmp_path}")
                    print(f"     Размер временного файла: {tmp_size} байт")
                    
                    if tmp_size != len(test_data):
                        print(f"     ВНИМАНИЕ: Размер временного файла ({tmp_size}) не совпадает с исходными данными ({len(test_data)})")
                    else:
                        print(f"     OK: Размер временного файла совпадает с исходными данными")
                    
                except Exception as e:
                    print(f"     ОШИБКА при создании временного файла: {e}")
                    continue
                
                # Тест 2: Проверка передачи данных в процедуру
                print(f"  2. Передача данных в хранимую процедуру:")
                try:
                    with open(tmp_path, 'rb') as tmp_file:
                        file_blob = tmp_file.read()
                    
                    print(f"     Прочитано из временного файла: {len(file_blob)} байт")
                    
                    if len(file_blob) != len(test_data):
                        print(f"     ВНИМАНИЕ: Прочитано {len(file_blob)} байт, ожидалось {len(test_data)}")
                    else:
                        print(f"     OK: Данные прочитаны полностью")
                    
                except Exception as e:
                    print(f"     ОШИБКА при чтении временного файла: {e}")
                    # Удаляем временный файл и переходим к следующему тесту
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
                    continue
                
                # Тест 3: Выполнение хранимой процедуры
                print(f"  3. Выполнение хранимой процедуры:")
                try:
                    sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.' || :imgext, :file_content)""")
                    
                    result = conn.execute(sql, {
                        'dir': img_path,
                        'modelid': modelid,
                        'imgext': imgext,
                        'file_content': file_blob
                    }).fetchall()
                    
                    print(f"     Процедура выполнена успешно")
                    print(f"     Результат: {result}")
                    
                except Exception as e:
                    print(f"     ОШИБКА при выполнении процедуры: {e}")
                    import traceback
                    print(f"     Трассировка: {traceback.format_exc()}")
                    # Удаляем временный файл и переходим к следующему тесту
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
                    continue
                
                # Тест 4: Проверка сохраненного файла
                print(f"  4. Проверка сохраненного файла:")
                try:
                    # Даем время на сохранение
                    time.sleep(2)
                    
                    full_path = os.path.join(img_path, filename)
                    
                    if os.path.exists(full_path):
                        saved_size = os.path.getsize(full_path)
                        print(f"     Файл сохранен: {full_path}")
                        print(f"     Размер сохраненного файла: {saved_size} байт")
                        
                        # Сравниваем размеры
                        print(f"     Сравнение размеров:")
                        print(f"       - Исходные данные: {len(test_data)} байт")
                        print(f"       - Временный файл: {tmp_size} байт")
                        print(f"       - Переданные данные: {len(file_blob)} байт")
                        print(f"       - Сохраненный файл: {saved_size} байт")
                        
                        if saved_size == len(test_data):
                            print(f"     OK: Размер сохраненного файла совпадает с исходными данными")
                        else:
                            print(f"     ВНИМАНИЕ: Размер сохраненного файла ({saved_size}) не совпадает с исходными данными ({len(test_data)})")
                            
                            # Проверяем содержимое файла
                            try:
                                with open(full_path, 'rb') as f:
                                    saved_data = f.read()
                                print(f"     Проверка содержимого:")
                                print(f"       - Первые 20 байт сохраненного файла: {saved_data[:20]}")
                                print(f"       - Первые 20 байт исходных данных: {test_data[:20]}")
                                
                                if saved_data == test_data:
                                    print(f"     OK: Содержимое файла совпадает с исходными данными")
                                else:
                                    print(f"     ВНИМАНИЕ: Содержимое файла НЕ совпадает с исходными данными")
                            except Exception as e:
                                print(f"     Ошибка при проверке содержимого файла: {e}")
                    else:
                        print(f"     ВНИМАНИЕ: Файл не сохранен: {full_path}")
                        print(f"     Проверьте права доступа к каталогу: {img_path}")
                
                except Exception as e:
                    print(f"     ОШИБКА при проверке сохраненного файла: {e}")
                
                # Очистка
                print(f"  5. Очистка:")
                try:
                    # Удаляем временный файл
                    os.unlink(tmp_path)
                    print(f"     Временный файл удален: {tmp_path}")
                    
                    # Пробуем удалить сохраненный файл (если есть права)
                    full_path = os.path.join(img_path, filename)
                    if os.path.exists(full_path):
                        try:
                            os.unlink(full_path)
                            print(f"     Сохраненный файл удален: {full_path}")
                        except Exception as e:
                            print(f"     Не удалось удалить сохраненный файл (нет прав): {e}")
                    
                except Exception as e:
                    print(f"     ОШИБКА при очистке: {e}")
                
                print(f"  --- Тест завершен ---")
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_file_sizes()
    if success:
        print("\n=== ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТЫ ЗАВЕРШЕНЫ С ОШИБКАМИ ===")
        sys.exit(1)