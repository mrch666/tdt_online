import sys
sys.path.append('.')
from app.database import engine
import os

try:
    with engine.connect() as conn:
        print("=== Test procedury wp_DeleteFile ===")
        
        # Тестовые данные
        base_dir = os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases')
        img_subdir = os.getenv('IMG_SUBDIR', 'img')
        img_path = os.path.join(base_dir, img_subdir)
        test_filename = "test_image.jpg"
        
        # Важно: путь должен заканчиваться на \ для правильной конкатенации
        if not img_path.endswith('\\'):
            img_path = img_path + '\\'
        
        print(f"Testovye dannye:")
        print(f"  img_path: {img_path}")
        print(f"  test_filename: {test_filename}")
        
        print(f"\n1. Test: vyzov procedury s pozicionnymi parametrami")
        try:
            # Пробуем с позиционными параметрами
            result = conn.execute(
                "SELECT * FROM \"wp_DeleteFile\"(?, ?)",
                [img_path, test_filename]
            )
            
            print("   Procedura vyzvana uspeshno!")
            
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
                if len(row) > 0:
                    oRes = row[0]
                    print(f"   oRes (rezultat): {oRes}")
                    if oRes == 1:
                        print("   USPESHNO! Procedura vernula 1 (uspeh)")
                    else:
                        print(f"   Procedura vernula {oRes} (mozhet byt', chto fail ne sushestvoval)")
            else:
                print("   Procedura ne vernula rezultat")
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n2. Test: vyzov procedury s 3 parametrami")
        try:
            # Пробуем с 3 параметрами (может быть, нужно 3?)
            result = conn.execute(
                "SELECT * FROM \"wp_DeleteFile\"(?, ?, ?)",
                [img_path, test_filename, None]
            )
            
            print("   Procedura vyzvana uspeshno!")
            
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n3. Test: proverka sushestvovaniya faila")
        full_path = os.path.join(img_path.rstrip('\\'), test_filename)
        if os.path.exists(full_path):
            print(f"   FAIL SUCHESTVUET: {full_path}")
        else:
            print(f"   FAIL NE SUCHESTVUET: {full_path}")
            
except Exception as e:
    print(f"Oshibka: {e}")
    import traceback
    traceback.print_exc()