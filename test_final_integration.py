import sys
sys.path.append('.')
from app.database import engine
import os

try:
    with engine.connect() as conn:
        print("=== Final integration test ===")
        
        # Тестовые данные
        base_dir = os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases')
        img_subdir = os.getenv('IMG_SUBDIR', 'img')
        img_path = os.path.join(base_dir, img_subdir)
        test_filename = "integration_test.jpg"
        test_data = b"integration test image data"
        
        # Важно: путь должен заканчиваться на \ для правильной конкатенации
        if not img_path.endswith('\\'):
            img_path = img_path + '\\'
        
        print(f"Testovye dannye:")
        print(f"  img_path: {img_path}")
        print(f"  test_filename: {test_filename}")
        print(f"  test_data: {len(test_data)} bayt")
        
        print(f"\n1. Sozdanie testovogo faila cherez wp_SaveBlobToFile:")
        try:
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(?, ?, ?)",
                [img_path, test_filename, test_data]
            )
            
            print("   Procedura vyzvana uspeshno!")
            
            row = result.fetchone()
            if row:
                success = row[0]
                if success == 1:
                    print("   USPESHNO! Fail sozdan.")
                else:
                    print(f"   OSHIBKA! Procedura vernula {success}")
            else:
                print("   Procedura ne vernula rezultat")
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n2. Proverka sozdannogo faila:")
        full_path = os.path.join(img_path.rstrip('\\'), test_filename)
        if os.path.exists(full_path):
            print(f"   FAIL SUCHESTVUET: {full_path}")
            print(f"   Razmer faila: {os.path.getsize(full_path)} bayt")
            
            try:
                with open(full_path, 'rb') as f:
                    content = f.read()
                print(f"   Soderzhimoe prochitano, dlina: {len(content)} bayt")
                if content == test_data:
                    print("   Soderzhimoe SOVPADAET s testovymi dannymi!")
                else:
                    print("   Soderzhimoe NE sovpadaet s testovymi dannymi")
            except Exception as e:
                print(f"   Oshibka chteniya faila: {e}")
        else:
            print(f"   FAIL NE SUCHESTVUET: {full_path}")
            
        print(f"\n3. Udalenie testovogo faila cherez wp_DeleteFile:")
        try:
            result = conn.execute(
                "SELECT * FROM \"wp_DeleteFile\"(?, ?)",
                [img_path, test_filename]
            )
            
            print("   Procedura vyzvana uspeshno!")
            
            row = result.fetchone()
            if row:
                success = row[0]
                if success == 1:
                    print("   USPESHNO! Procedura udaleniya vernula 1.")
                else:
                    print(f"   Procedura udaleniya vernula {success}")
            else:
                print("   Procedura ne vernula rezultat")
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n4. Proverka udaleniya faila:")
        if os.path.exists(full_path):
            print(f"   FAIL VSE ESHCHE SUCHESTVUET: {full_path}")
            print("   OSHIBKA! Fail ne udalen!")
        else:
            print(f"   FAIL USPEHNO UDALEN: {full_path}")
            print("   USPESHNO! Vse rabotaet pravilno!")
            
        print(f"\n5. Proverka staryh oshibok:")
        print("   a) Staraya oshibka s parametrami :path, :filename, :data:")
        try:
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(:path, :filename, :data)",
                {"path": img_path, "filename": test_filename, "data": test_data}
            )
            print("      Rabotaet (neozhidanno!)")
        except Exception as e:
            print(f"      Ne rabotaet (ozhidanno): {str(e)[:100]}...")
            
        print("   b) Staraya oshibka s :iPathDB, :iPath, :iBlob:")
        try:
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(:iPathDB, :iPath, :iBlob)",
                {"iPathDB": img_path, "iPath": test_filename, "iBlob": test_data}
            )
            print("      Rabotaet (neozhidanno!)")
        except Exception as e:
            print(f"      Ne rabotaet (ozhidanno): {str(e)[:100]}...")
            
except Exception as e:
    print(f"Oshibka: {e}")
    import traceback
    traceback.print_exc()