import sys
sys.path.append('.')
from app.database import engine
import os

try:
    with engine.connect() as conn:
        print("=== Test ispravlennogo koda ===")
        
        # Тестовые данные
        base_dir = os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases')
        img_subdir = os.getenv('IMG_SUBDIR', 'img')
        img_path = os.path.join(base_dir, img_subdir)
        test_filename = "test_image.jpg"
        test_data = b"test image data"
        
        print(f"Testovye dannye:")
        print(f"  img_path: {img_path}")
        print(f"  test_filename: {test_filename}")
        
        # Важно: путь должен заканчиваться на \ для правильной конкатенации в процедуре
        if not img_path.endswith('\\'):
            img_path = img_path + '\\'
            print(f"  Dobavlen \\ v konce puti: {img_path}")
        
        print(f"\n1. Test procedury wp_SaveBlobToFile s pravil'nymi parametrami:")
        try:
            # Пробуем вызвать процедуру с правильным порядком параметров
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(:oRes, :iPathDB, :iPath, :iBlob)",
                {
                    "oRes": None,         # Выходной параметр
                    "iPathDB": img_path,  # Путь к папке
                    "iPath": test_filename,  # Имя файла
                    "iBlob": test_data    # Данные файла
                }
            )
            
            print("   Procedura vyzvana uspeshno!")
            
            # Получаем результат
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
                if len(row) > 0:
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
            
        print(f"\n2. Test procedury wp_DeleteFile s pravil'nymi parametrami:")
        try:
            result = conn.execute(
                "SELECT * FROM \"wp_DeleteFile\"(:oRes, :iPathDB, :iPath)",
                {
                    "oRes": None,
                    "iPathDB": img_path,
                    "iPath": test_filename
                }
            )
            
            print("   Procedura vyzvana uspeshno!")
            
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
                if len(row) > 0:
                    oRes = row[0]
                    print(f"   oRes (rezultat): {oRes}")
            else:
                print("   Procedura ne vernula rezultat")
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n3. Proverka sushestvovaniya faila posle sohraneniya:")
        full_path = os.path.join(img_path.rstrip('\\'), test_filename)
        if os.path.exists(full_path):
            print(f"   FAIL SUCHESTVUET: {full_path}")
            print(f"   Razmer faila: {os.path.getsize(full_path)} bayt")
            
            # Пробуем прочитать файл
            try:
                with open(full_path, 'rb') as f:
                    content = f.read()
                print(f"   Soderzhimoe prochitano uspeshno, dlina: {len(content)} bayt")
                if content == test_data:
                    print("   Soderzhimoe sovpadaet s testovymi dannymi!")
                else:
                    print("   Soderzhimoe NE sovpadaet s testovymi dannymi")
            except Exception as e:
                print(f"   Oshibka chteniya faila: {e}")
        else:
            print(f"   FAIL NE SUCHESTVUET: {full_path}")
            
except Exception as e:
    print(f"Oshibka: {e}")
    import traceback
    traceback.print_exc()