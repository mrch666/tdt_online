import sys
sys.path.append('.')
import os
import logging
from app.database import engine

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_param_types():
    """Тест передачи параметров разных типов в хранимую процедуру"""
    print("=== Тест передачи параметров в хранимую процедуру ===")
    
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
            print(f"  - img_path: {img_path} (type: {type(img_path)})")
            print(f"  - filename: {filename} (type: {type(filename)})")
            print(f"  - test_data: <binary data 100 bytes>")
            
            # Тестовые бинарные данные
            test_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f'
            
            # Тест 1: как кортеж
            print(f"\n1. Тест передачи параметров как кортеж:")
            try:
                result = conn.execute(
                    'SELECT * FROM "wp_SaveBlobToFile"(?, ?, ?)',
                    (img_path, filename, test_data)
                )
                print(f"   УСПЕХ: Параметры переданы как кортеж")
                conn.rollback()  # Откатываем, так как это тест
            except Exception as e:
                print(f"   ОШИБКА: {e}")
                print(f"   Тип ошибки: {type(e)}")
            
            # Тест 2: как список кортежей
            print(f"\n2. Тест передачи параметров как список кортежей:")
            try:
                result = conn.execute(
                    'SELECT * FROM "wp_SaveBlobToFile"(?, ?, ?)',
                    [(img_path, filename, test_data)]
                )
                print(f"   УСПЕХ: Параметры переданы как список кортежей")
                conn.rollback()
            except Exception as e:
                print(f"   ОШИБКА: {e}")
                print(f"   Тип ошибки: {type(e)}")
            
            # Тест 3: как именованные параметры
            print(f"\n3. Тест передачи параметров как именованные параметры:")
            try:
                result = conn.execute(
                    'SELECT * FROM "wp_SaveBlobToFile"(:p1, :p2, :p3)',
                    {"p1": img_path, "p2": filename, "p3": test_data}
                )
                print(f"   УСПЕХ: Параметры переданы как именованные параметры")
                conn.rollback()
            except Exception as e:
                print(f"   ОШИБКА: {e}")
                print(f"   Тип ошибки: {type(e)}")
            
            # Тест 4: проверка типов параметров
            print(f"\n4. Проверка типов параметров:")
            print(f"   img_path тип: {type(img_path)}, значение: {repr(img_path)}")
            print(f"   filename тип: {type(filename)}, значение: {repr(filename)}")
            print(f"   test_data тип: {type(test_data)}, длина: {len(test_data)}")
            
            # Тест 5: явное преобразование типов
            print(f"\n5. Тест с явным преобразованием типов:")
            try:
                param1 = str(img_path)
                param2 = str(filename)
                param3 = bytes(test_data)
                
                print(f"   Преобразованные параметры:")
                print(f"     param1: {type(param1)} = {repr(param1)}")
                print(f"     param2: {type(param2)} = {repr(param2)}")
                print(f"     param3: {type(param3)} = длина {len(param3)} байт")
                
                result = conn.execute(
                    'SELECT * FROM "wp_SaveBlobToFile"(?, ?, ?)',
                    (param1, param2, param3)
                )
                print(f"   УСПЕХ: Параметры с явным преобразованием типов")
                conn.rollback()
            except Exception as e:
                print(f"   ОШИБКА: {e}")
                print(f"   Тип ошибки: {type(e)}")
                import traceback
                print(f"   Трассировка: {traceback.format_exc()}")
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_param_types()
    if success:
        print("\n=== ТЕСТ ЗАВЕРШЕН ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ ===")
        sys.exit(1)