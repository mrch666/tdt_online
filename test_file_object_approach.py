import sys
sys.path.append('.')
from app.database import engine
import os
import tempfile

try:
    with engine.connect() as conn:
        print("=== Test s peredachej ob'ekta faila (kak v kode opisaniy) ===")
        
        # Тестовые данные
        base_dir = os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases')
        img_subdir = os.getenv('IMG_SUBDIR', 'img')
        img_path = os.path.join(base_dir, img_subdir) + os.sep
        test_filename = "test_file_object.jpg"
        test_data = b"test image data file object approach"
        
        print(f"Testovye dannye:")
        print(f"  img_path: {img_path}")
        print(f"  test_filename: {test_filename}")
        print(f"  test_data: {len(test_data)} bayt")
        
        print(f"\n1. Test: s peredachej ob'ekta faila (kak v kode opisaniy):")
        try:
            # Создаем временный файл
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_path = temp_file.name
            
            try:
                # Записываем тестовые данные
                with open(temp_path, 'wb') as f:
                    f.write(test_data)
                
                # Формируем SQL запрос
                sql = f"""SELECT * FROM \"wp_SaveBlobToFile\"('{img_path}', '{test_filename}', :zip_file)"""
                print(f"   SQL zapros: {sql}")
                
                # Пробуем передать объект файла (как в коде описаний)
                with open(temp_path, 'rb') as image_file:
                    result = conn.execute(sql, {"zip_file": image_file})
                
                print("   Procedura vyzvana uspeshno!")
                
                row = result.fetchone()
                if row:
                    success = row[0]
                    if success == 1:
                        print("   USPESHNO! Procedura vernula 1 (uspeh)")
                    else:
                        print(f"   OSHIBKA! Procedura vernula {success}")
                else:
                    print("   Procedura ne vernula rezultat")
                    
            except Exception as e:
                print(f"   OSHIBKA: {e}")
            finally:
                temp_file.close()
                try:
                    os.unlink(temp_path)
                except:
                    pass
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n2. Test: s pozicionnymi parametrami (kak rabotalo ranee):")
        try:
            # Позиционные параметры
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(?, ?, ?)",
                [img_path, test_filename, test_data]
            )
            
            print("   Procedura vyzvana uspeshno!")
            
            row = result.fetchone()
            if row:
                success = row[0]
                if success == 1:
                    print("   USPESHNO! Procedura vernula 1 (uspeh)")
                else:
                    print(f"   OSHIBKA! Procedura vernula {success}")
            else:
                print("   Procedura ne vernula rezultat")
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n3. Test: proverka sozdannogo faila:")
        full_path = os.path.join(img_path.rstrip(os.sep), test_filename)
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
            
        print(f"\n4. Test: udalenie faila:")
        try:
            sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', '{test_filename}')"""
            result = conn.execute(sql)
            
            print("   Procedura vyzvana uspeshno!")
            
            row = result.fetchone()
            if row:
                success = row[0]
                print(f"   Rezultat udaleniya: {success}")
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
except Exception as e:
    print(f"Oshibka: {e}")
    import traceback
    traceback.print_exc()