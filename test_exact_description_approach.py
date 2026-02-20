import sys
sys.path.append('.')
from app.database import engine
import os
import tempfile

try:
    with engine.connect() as conn:
        print("=== Test tochnogo podhoda iz zagruzki opisaniy ===")
        
        # Тестовые данные
        base_dir = os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases')
        img_subdir = os.getenv('IMG_SUBDIR', 'img')
        img_path = os.path.join(base_dir, img_subdir) + os.sep
        test_modelid = "1"  # Тестовый ID модели
        test_data = b"test image data exact approach"
        
        print(f"Testovye dannye:")
        print(f"  img_path: {img_path}")
        print(f"  test_modelid: {test_modelid}")
        print(f"  test_data: {len(test_data)} bayt")
        
        print(f"\n1. Test: kak v kode opisaniy (s dec64i0 i dec64i1):")
        try:
            # Создаем временный файл
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_path = temp_file.name
            
            try:
                # Записываем тестовые данные
                with open(temp_path, 'wb') as f:
                    f.write(test_data)
                
                # Формируем SQL запрос ТОЧНО как в коде описаний
                # В коде описаний: f"""SELECT * FROM \"wp_SaveBlobToFile\"('{desc_dir}', dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.dat',:zip_file)"""
                sql = f"""SELECT * FROM \"wp_SaveBlobToFile\"('{img_path}', dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.jpg', :image_data)"""
                print(f"   SQL zapros: {sql}")
                
                # Читаем данные из файла
                with open(temp_path, 'rb') as image_file:
                    image_data = image_file.read()
                
                # Выполняем запрос
                result = conn.execute(sql, {"modelid": test_modelid, "image_data": image_data})
                
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
            
        print(f"\n2. Test: proverka kak rabotaet kod opisaniy s zip_file:")
        try:
            # Тестируем подход из кода описаний с zip_file параметром
            sql = f"""SELECT * FROM \"wp_SaveBlobToFile\"('{img_path}', 'test_exact.jpg', :zip_file)"""
            print(f"   SQL zapros: {sql}")
            
            result = conn.execute(sql, {"zip_file": test_data})
            
            print("   Procedura vyzvana uspeshno!")
            
            row = result.fetchone()
            if row:
                success = row[0]
                print(f"   Rezultat: {success}")
            else:
                print("   Procedura ne vernula rezultat")
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n3. Test: proverka s parametrom :data (kak v starom kode):")
        try:
            sql = f"""SELECT * FROM \"wp_SaveBlobToFile\"('{img_path}', 'test_data.jpg', :data)"""
            print(f"   SQL zapros: {sql}")
            
            result = conn.execute(sql, {"data": test_data})
            
            print("   Procedura vyzvana uspeshno!")
            
            row = result.fetchone()
            if row:
                success = row[0]
                print(f"   Rezultat: {success}")
            else:
                print("   Procedura ne vernula rezultat")
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n4. Test: proverka s parametrom :iBlob (kak v strukture procedury):")
        try:
            sql = f"""SELECT * FROM \"wp_SaveBlobToFile\"('{img_path}', 'test_iblob.jpg', :iBlob)"""
            print(f"   SQL zapros: {sql}")
            
            result = conn.execute(sql, {"iBlob": test_data})
            
            print("   Procedura vyzvana uspeshno!")
            
            row = result.fetchone()
            if row:
                success = row[0]
                print(f"   Rezultat: {success}")
            else:
                print("   Procedura ne vernula rezultat")
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
except Exception as e:
    print(f"Oshibka: {e}")
    import traceback
    traceback.print_exc()