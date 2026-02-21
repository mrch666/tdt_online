import sys
sys.path.append('.')
import os
import logging
from app.database import engine
from sqlalchemy import text, bindparam, String, LargeBinary

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_procedure_without_fetchone():
    """Тест выполнения хранимой процедуры без fetchone"""
    print("=== Тест выполнения хранимой процедуры без fetchone ===")
    
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
            
            # Создаем тестовый GIF файл (минимальный валидный GIF)
            test_data = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01D\x00;'
            
            # Тест 1: Пробуем выполнить процедуру без fetchone
            print(f"\n1. Выполняем хранимую процедуру без fetchone:")
            try:
                stmt = text("SELECT * FROM \"wp_SaveBlobToFile\"(:p1, :p2, :p3)")
                
                # Явно указываем типы параметров через bindparams
                stmt = stmt.bindparams(
                    bindparam("p1", value=img_path, type_=String),
                    bindparam("p2", value=filename, type_=String),
                    bindparam("p3", value=test_data, type_=LargeBinary)
                )
                
                # Выполняем без получения результата
                result = conn.execute(stmt, {"p1": img_path, "p2": filename, "p3": test_data})
                
                print(f"   УСПЕХ: Процедура выполнена без ошибок")
                print(f"   Результат выполнения: {result}")
                print(f"   Тип результата: {type(result)}")
                
                # Проверяем, что файл создался
                import time
                time.sleep(0.5)  # Даем время на сохранение
                
                full_path = os.path.join(img_path, filename)
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    print(f"   Файл создан: {full_path}")
                    print(f"   Размер файла: {file_size} байт")
                    
                    # Удаляем тестовый файл (если есть права)
                    try:
                        os.remove(full_path)
                        print(f"   Тестовый файл удален")
                    except Exception as e:
                        print(f"   Предупреждение: не удалось удалить тестовый файл: {e}")
                else:
                    print(f"   Файл не создан: {full_path}")
                    print(f"   Проверьте права доступа к каталогу")
                    
            except Exception as e:
                print(f"   ОШИБКА при выполнении процедуры: {e}")
                import traceback
                print(f"   Трассировка: {traceback.format_exc()}")
                return False
            
            # Тест 2: Проверяем, что процедура действительно не возвращает результат
            print(f"\n2. Проверяем, что процедура не возвращает результат:")
            try:
                stmt = text("SELECT * FROM \"wp_SaveBlobToFile\"(:p1, :p2, :p3)")
                
                stmt = stmt.bindparams(
                    bindparam("p1", value=img_path, type_=String),
                    bindparam("p2", value=filename, type_=String),
                    bindparam("p3", value=test_data, type_=LargeBinary)
                )
                
                # Пробуем получить результат (должна быть ошибка)
                result = conn.execute(stmt, {"p1": img_path, "p2": filename, "p3": test_data})
                try:
                    proc_result = result.fetchone()
                    print(f"   ВНИМАНИЕ: Процедура вернула результат: {proc_result}")
                    print(f"   Это означает, что процедура возвращает данные")
                except Exception as fetch_error:
                    print(f"   ОЖИДАЕМО: Не удалось получить результат: {fetch_error}")
                    print(f"   Это нормально для процедур, которые не возвращают данные")
                
                conn.commit()
                
            except Exception as e:
                print(f"   ОШИБКА: {e}")
                import traceback
                print(f"   Трассировка: {traceback.format_exc()}")
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_procedure_without_fetchone()
    if success:
        print("\n=== ТЕСТ ЗАВЕРШЕН УСПЕШНО ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ ===")
        sys.exit(1)