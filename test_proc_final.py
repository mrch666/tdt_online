import sys
sys.path.append('.')
from app.database import engine
import os

try:
    with engine.connect() as conn:
        print("=== Final test procedur ===")
        
        # Тестовые данные
        base_dir = os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases')
        img_subdir = os.getenv('IMG_SUBDIR', 'img')
        img_path = os.path.join(base_dir, img_subdir)
        test_filename = "test_image.jpg"
        test_data = b"test image data"
        
        # Важно: путь должен заканчиваться на \ для правильной конкатенации
        if not img_path.endswith('\\'):
            img_path = img_path + '\\'
        
        print(f"Testovye dannye:")
        print(f"  img_path: {img_path}")
        print(f"  test_filename: {test_filename}")
        
        print(f"\n1. Test: vyzov procedury bez vyhodnogo parametra oRes")
        try:
            # Пробуем вызвать процедуру только с входными параметрами
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(:iPathDB, :iPath, :iBlob)",
                {
                    "iPathDB": img_path,
                    "iPath": test_filename,
                    "iBlob": test_data
                }
            )
            
            print("   Procedura vyzvana uspeshno!")
            
            # Получаем результат
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
                if len(row) > 0:
                    # Первое поле в результате - это oRes
                    oRes = row[0]
                    print(f"   oRes (rezultat): {oRes}")
                    if oRes == 1:
                        print("   USPESHNO! Procedura vernula 1 (uspeh)")
                    else:
                        print(f"   OSHIBKA! Procedura vernula {oRes}")
            else:
                print("   Procedura ne vernula rezultat")
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n2. Test: vyzov procedury s pozicionnymi parametrami")
        try:
            # Пробуем с позиционными параметрами
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(?, ?, ?)",
                [img_path, test_filename, test_data]
            )
            
            print("   Procedura vyzvana uspeshno!")
            
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
            else:
                print("   Procedura ne vernula rezultat")
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n3. Test: proverka kak rabotal staryj kod")
        try:
            # Пробуем как в оригинальном коде (с ошибкой)
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(:path, :filename, :data)",
                {
                    "path": img_path,
                    "filename": test_filename,
                    "data": test_data
                }
            )
            
            print("   Staryj kod rabotaet!")
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
        except Exception as e:
            print(f"   OSHIBKA staryj kod: {e}")
            
        print(f"\n4. Test: proverka sushestvuyushih vyzovov v baze")
        try:
            # Ищем реальные вызовы процедуры в базе
            result = conn.execute("""
                SELECT FIRST 1 
                    RDB$PROCEDURE_SOURCE 
                FROM RDB$PROCEDURES 
                WHERE RDB$PROCEDURE_SOURCE LIKE '%wp_SaveBlobToFile(%'
            """)
            
            proc_with_call = result.fetchone()
            if proc_with_call and proc_with_call[0]:
                source = proc_with_call[0]
                # Ищем строку с вызовом
                lines = source.split('\n')
                for line in lines:
                    if 'wp_SaveBlobToFile' in line and '(' in line and ')' in line:
                        print(f"   Nayden vyzov: {line.strip()}")
                        break
            else:
                print("   Net vyzovov v procedurah")
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
except Exception as e:
    print(f"Oshibka: {e}")
    import traceback
    traceback.print_exc()