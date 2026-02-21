import sys
sys.path.append('.')
import os
import logging
from app.database import engine
from sqlalchemy import text, bindparam, String, LargeBinary

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_procedure_access():
    """Тест доступа хранимой процедуры к файловой системе"""
    print("=== Тест доступа хранимой процедуры к файловой системе ===")
    
    modelid = "000001002Qa{"
    imgext = "jpg"
    
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
            print(f"  - Каталог существует: {os.path.exists(img_path)}")
            
            # Проверяем содержимое каталога
            if os.path.exists(img_path):
                files = os.listdir(img_path)
                print(f"  - Файлов в каталоге: {len(files)}")
                if files:
                    print(f"  - Примеры файлов: {files[:5]}")
            
            # Создаем тестовые данные (маленький JPEG)
            test_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xf9\xff\x00\xff\xd9'
            
            # Тест 1: Пробуем выполнить процедуру
            print(f"\n1. Выполняем хранимую процедуру:")
            try:
                stmt = text("SELECT * FROM \"wp_SaveBlobToFile\"(:p1, :p2, :p3)")
                
                stmt = stmt.bindparams(
                    bindparam("p1", value=img_path, type_=String),
                    bindparam("p2", value=filename, type_=String),
                    bindparam("p3", value=test_data, type_=LargeBinary)
                )
                
                result = conn.execute(stmt, {"p1": img_path, "p2": filename, "p3": test_data})
                
                print(f"   Процедура выполнена")
                print(f"   Результат: {result}")
                
                # Пробуем получить результат
                try:
                    proc_result = result.fetchone()
                    print(f"   Результат процедуры: {proc_result}")
                except Exception as fetch_error:
                    print(f"   Не удалось получить результат: {fetch_error}")
                
            except Exception as e:
                print(f"   ОШИБКА при выполнении процедуры: {e}")
                import traceback
                print(f"   Трассировка: {traceback.format_exc()}")
                return False
            
            # Проверяем, что файл создался
            import time
            time.sleep(1)  # Даем больше времени на сохранение
            
            full_path = os.path.join(img_path, filename)
            print(f"\n2. Проверяем создание файла:")
            print(f"   Полный путь: {full_path}")
            print(f"   Файл существует: {os.path.exists(full_path)}")
            
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                print(f"   Файл создан: {full_path}")
                print(f"   Размер файла: {file_size} байт")
                
                # Проверяем содержимое файла
                try:
                    with open(full_path, 'rb') as f:
                        file_data = f.read()
                    print(f"   Прочитано: {len(file_data)} байт")
                    print(f"   Первые 20 байт: {file_data[:20]}")
                    
                    # Удаляем тестовый файл (если есть права)
                    try:
                        os.remove(full_path)
                        print(f"   Тестовый файл удален")
                    except Exception as e:
                        print(f"   Предупреждение: не удалось удалить тестовый файл: {e}")
                except Exception as e:
                    print(f"   Ошибка при чтении файла: {e}")
            else:
                print(f"   ФАЙЛ НЕ СОЗДАН!")
                print(f"   Возможные причины:")
                print(f"     1. Нет прав на запись в каталог")
                print(f"     2. Хранимая процедура не работает")
                print(f"     3. Неправильный путь к каталогу")
                print(f"     4. Служба Firebird не имеет доступа к файловой системе")
                
                # Проверяем альтернативный путь
                alt_path = "C:\\temp\\"
                if os.path.exists(alt_path):
                    print(f"\n3. Пробуем альтернативный каталог: {alt_path}")
                    alt_filename = f"test_{filename}"
                    alt_full_path = os.path.join(alt_path, alt_filename)
                    
                    try:
                        stmt = text("SELECT * FROM \"wp_SaveBlobToFile\"(:p1, :p2, :p3)")
                        
                        stmt = stmt.bindparams(
                            bindparam("p1", value=alt_path, type_=String),
                            bindparam("p2", value=alt_filename, type_=String),
                            bindparam("p3", value=test_data, type_=LargeBinary)
                        )
                        
                        result = conn.execute(stmt, {"p1": alt_path, "p2": alt_filename, "p3": test_data})
                        print(f"   Процедура выполнена для альтернативного пути")
                        
                        time.sleep(1)
                        if os.path.exists(alt_full_path):
                            print(f"   Файл создан в альтернативном каталоге!")
                            try:
                                os.remove(alt_full_path)
                                print(f"   Тестовый файл удален")
                            except Exception as e:
                                print(f"   Не удалось удалить файл: {e}")
                        else:
                            print(f"   Файл не создан и в альтернативном каталоге")
                            print(f"   Вероятно, проблема в хранимой процедуре")
                    except Exception as e:
                        print(f"   Ошибка при выполнении процедуры для альтернативного пути: {e}")
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_procedure_access()
    if success:
        print("\n=== ТЕСТ ЗАВЕРШЕН УСПЕШНО ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ ===")
        sys.exit(1)