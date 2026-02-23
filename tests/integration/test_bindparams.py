import sys
sys.path.append('.')
import os
import logging
from app.database import engine
from sqlalchemy import text, bindparam, String, LargeBinary

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_bindparams():
    """Тест передачи параметров с bindparams"""
    print("=== Тест передачи параметров с bindparams ===")
    
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
            
            # Тестовые бинарные данные
            test_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f'
            
            # Тест с bindparams
            print(f"\n1. Тест с bindparams:")
            try:
                stmt = text("SELECT * FROM \"wp_SaveBlobToFile\"(:p1, :p2, :p3)")
                
                # Явно указываем типы параметров через bindparams
                stmt = stmt.bindparams(
                    bindparam("p1", value=img_path, type_=String),
                    bindparam("p2", value=filename, type_=String),
                    bindparam("p3", value=test_data, type_=LargeBinary)
                )
                
                result = conn.execute(stmt, {"p1": img_path, "p2": filename, "p3": test_data})
                print(f"   УСПЕХ: Параметры переданы с bindparams")
                # Не делаем commit, так как это тест
            except Exception as e:
                print(f"   ОШИБКА: {e}")
                print(f"   Тип ошибки: {type(e)}")
                import traceback
                print(f"   Трассировка: {traceback.format_exc()}")
                return False
            
            # Тест без bindparams (для сравнения)
            print(f"\n2. Тест без bindparams (старый способ):")
            try:
                result = conn.execute(
                    'SELECT * FROM "wp_SaveBlobToFile"(?, ?, ?)',
                    (img_path, filename, test_data)
                )
                print(f"   УСПЕХ: Параметры переданы без bindparams")
            except Exception as e:
                print(f"   ОШИБКА: {e}")
                print(f"   Тип ошибки: {type(e)}")
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_bindparams()
    if success:
        print("\n=== ТЕСТ ЗАВЕРШЕН УСПЕШНО ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ ===")
        sys.exit(1)