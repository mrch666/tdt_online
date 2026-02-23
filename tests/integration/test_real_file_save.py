import sys
sys.path.append('.')
import os
import logging
from app.database import engine
from sqlalchemy import text, bindparam, String, LargeBinary
import tempfile
import shutil

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_real_file_save():
    """Тест реального сохранения файла через хранимую процедуру"""
    print("=== Тест реального сохранения файла ===")
    
    modelid = "000001002Qa{"
    imgext = "gif"
    
    try:
        with engine.connect() as conn:
            # Получаем числовые части ID
            id_parts_result = conn.execute(
                'SELECT DEC64I0("id"), DEC64I1("id") FROM "modelgoods" WHERE "id" = ?',
                [modelid]
            ).fetchone()
            
            if not id_parts_result:
                print("ОШИБКА: Не удалось получить части ID")
                return False
                
            part0 = id_parts_result[0]
            part1 = id_parts_result[1]
            filename = f"{part0}_{part1}.{imgext}"
            img_path = os.path.join(os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases'), 
                                   os.getenv('IMG_SUBDIR', 'img')) + os.sep
            
            print(f"Параметры для теста:")
            print(f"  - img_path: {img_path}")
            print(f"  - filename: {filename}")
            print(f"  - Проверяем существование каталога: {os.path.exists(img_path)}")
            
            # Создаем тестовый GIF файл (минимальный валидный GIF)
            test_data = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01D\x00;'
            
            # Проверяем путь перед сохранением
            full_path = os.path.join(img_path, filename)
            print(f"  - Полный путь к файлу: {full_path}")
            print(f"  - Файл существует до сохранения: {os.path.exists(full_path)}")
            
            # Тест 1: Пробуем сохранить файл
            print(f"\n1. Пробуем сохранить файл через хранимую процедуру:")
            try:
                stmt = text("SELECT * FROM \"wp_SaveBlobToFile\"(:p1, :p2, :p3)")
                
                # Явно указываем типы параметров через bindparams
                stmt = stmt.bindparams(
                    bindparam("p1", value=img_path, type_=String),
                    bindparam("p2", value=filename, type_=String),
                    bindparam("p3", value=test_data, type_=LargeBinary)
                )
                
                result = conn.execute(stmt, {"p1": img_path, "p2": filename, "p3": test_data})
                
                # Получаем результат выполнения процедуры
                proc_result = result.fetchone()
                print(f"   Результат процедуры: {proc_result}")
                
                # Проверяем, что файл создался
                import time
                time.sleep(0.5)  # Даем время на сохранение
                
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    print(f"   УСПЕХ: Файл создан: {full_path}")
                    print(f"   Размер файла: {file_size} байт")
                    
                    # Читаем файл и сравниваем с отправленными данными
                    with open(full_path, 'rb') as f:
                        saved_data = f.read()
                    
                    if saved_data == test_data:
                        print(f"   УСПЕХ: Данные файла совпадают с отправленными")
                    else:
                        print(f"   ОШИБКА: Данные файла не совпадают")
                        print(f"     Отправлено: {len(test_data)} байт")
                        print(f"     Сохранено: {len(saved_data)} байт")
                        
                    # Удаляем тестовый файл
                    try:
                        os.remove(full_path)
                        print(f"   Тестовый файл удален")
                    except Exception as e:
                        print(f"   Предупреждение: не удалось удалить тестовый файл: {e}")
                else:
                    print(f"   ОШИБКА: Файл не создан: {full_path}")
                    print(f"   Проверьте права доступа к каталогу: {img_path}")
                    print(f"   Проверьте работу хранимой процедуры wp_SaveBlobToFile")
                    
                    # Проверяем права на запись
                    test_file_path = os.path.join(img_path, "test_write.tmp")
                    try:
                        with open(test_file_path, 'wb') as f:
                            f.write(b'test')
                        print(f"   Права на запись в каталог: ЕСТЬ")
                        os.remove(test_file_path)
                    except Exception as e:
                        print(f"   Права на запись в каталог: НЕТ ({e})")
                    
                    return False
                    
            except Exception as e:
                print(f"   ОШИБКА при выполнении процедуры: {e}")
                import traceback
                print(f"   Трассировка: {traceback.format_exc()}")
                return False
            
            # Тест 2: Проверяем работу процедуры wp_DeleteFile
            print(f"\n2. Проверяем работу процедуры удаления файла:")
            try:
                # Сначала создаем файл для удаления
                test_delete_file = os.path.join(img_path, "test_delete.tmp")
                with open(test_delete_file, 'wb') as f:
                    f.write(b'test data for deletion')
                
                print(f"   Создан тестовый файл для удаления: {test_delete_file}")
                print(f"   Файл существует: {os.path.exists(test_delete_file)}")
                
                # Удаляем через хранимую процедуру
                sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', 'test_delete.tmp')"""
                result = conn.execute(text(sql))
                proc_result = result.fetchone()
                print(f"   Результат процедуры удаления: {proc_result}")
                
                # Проверяем, что файл удален
                import time
                time.sleep(0.5)
                
                if os.path.exists(test_delete_file):
                    print(f"   ОШИБКА: Файл не удален")
                    # Пробуем удалить обычным способом
                    try:
                        os.remove(test_delete_file)
                        print(f"   Файл удален обычным способом")
                    except Exception as e:
                        print(f"   Не удалось удалить файл: {e}")
                    return False
                else:
                    print(f"   УСПЕХ: Файл успешно удален через хранимую процедуру")
                    
            except Exception as e:
                print(f"   ОШИБКА при удалении файла: {e}")
                import traceback
                print(f"   Трассировка: {traceback.format_exc()}")
                
                # Пробуем удалить файл обычным способом
                if os.path.exists(test_delete_file):
                    try:
                        os.remove(test_delete_file)
                        print(f"   Файл удален обычным способом")
                    except Exception as e2:
                        print(f"   Не удалось удалить файл: {e2}")
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_real_file_save()
    if success:
        print("\n=== ТЕСТ ЗАВЕРШЕН УСПЕШНО ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ ===")
        sys.exit(1)