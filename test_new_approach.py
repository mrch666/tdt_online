import sys
sys.path.append('.')
from app.database import engine
import os
import tempfile

try:
    with engine.connect() as conn:
        print("=== Test novogo podhoda (analogichno zagruzke opisaniy) ===")
        
        # Тестовые данные
        base_dir = os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases')
        img_subdir = os.getenv('IMG_SUBDIR', 'img')
        img_path = os.path.join(base_dir, img_subdir) + os.sep
        test_filename = "test_new_approach.jpg"
        test_data = b"test image data for new approach"
        
        print(f"Testovye dannye:")
        print(f"  img_path: {img_path}")
        print(f"  test_filename: {test_filename}")
        print(f"  test_data: {len(test_data)} bayt")
        
        print(f"\n1. Test: sozdanie vremennogo faila i vyzov procedury:")
        try:
            # Создаем временный файл
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_path = temp_file.name
            
            try:
                # Записываем тестовые данные
                with open(temp_path, 'wb') as f:
                    f.write(test_data)
                
                # Формируем SQL запрос аналогично загрузке описаний
                sql = f"""SELECT * FROM \"wp_SaveBlobToFile\"('{img_path}', '{test_filename}', :image_data)"""
                print(f"   SQL zapros: {sql}")
                
                # Читаем данные из файла
                with open(temp_path, 'rb') as image_file:
                    image_data = image_file.read()
                
                # Выполняем запрос
                result = conn.execute(sql, {"image_data": image_data})
                
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
            
        print(f"\n2. Test: udalenie faila cherez proceduru:")
        try:
            sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', '{test_filename}')"""
            print(f"   SQL zapros: {sql}")
            
            result = conn.execute(sql)
            
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
            
        print(f"\n3. Proverka sozdannogo faila:")
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
            
        print(f"\n4. Proverka udaleniya faila:")
        if os.path.exists(full_path):
            print(f"   FAIL VSE ESHCHE SUCHESTVUET: {full_path}")
        else:
            print(f"   FAIL USPEHNO UDALEN: {full_path}")
            
except Exception as e:
    print(f"Oshibka: {e}")
    import traceback
    traceback.print_exc()