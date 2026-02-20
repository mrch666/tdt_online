import sys
sys.path.append('.')
from app.database import engine
import os

try:
    with engine.connect() as conn:
        # Тестовые данные
        base_dir = os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases')
        img_subdir = os.getenv('IMG_SUBDIR', 'img')
        img_path = os.path.join(base_dir, img_subdir)
        test_filename = "test_image.jpg"
        full_path = os.path.join(img_path, test_filename)
        test_data = b"test image data"
        
        print(f"Testovye dannye:")
        print(f"  img_path (papka): {img_path}")
        print(f"  test_filename: {test_filename}")
        print(f"  full_path: {full_path}")
        
        # В Firebird есть два способа вызова процедуры:
        # 1. SELECT * FROM procedure_name(...) - если процедура возвращает результат
        # 2. EXECUTE PROCEDURE procedure_name(...) - если процедура не возвращает результат или возвращает через выходные параметры
        
        print(f"\n1. Variant: EXECUTE PROCEDURE (dlya procedur, kotorye ne vozvraschayut rezultat)")
        try:
            # EXECUTE PROCEDURE используется для процедур, которые могут изменять данные
            result = conn.execute(
                "EXECUTE PROCEDURE \"wp_SaveBlobToFile\"(:iPathDB, :oRes, :iPath, :iBlob)",
                {
                    "iPathDB": img_path,
                    "oRes": None,
                    "iPath": test_filename,
                    "iBlob": test_data
                }
            )
            print("   Uspeshno!")
            # Для EXECUTE PROCEDURE может не быть результата
            try:
                row = result.fetchone()
                if row:
                    print(f"   Rezultat: {row}")
            except:
                print("   Net rezultata dlya chteniya (mozhet byt', chto procedura ne vozvraschaet rezultat)")
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n2. Variant: SELECT * FROM (dlya procedur, kotorye vozvraschayut rezultat)")
        try:
            # Может быть, процедура ожидает параметры в другом порядке
            # Попробуем разные порядки параметров
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(:param1, :param2, :param3, :param4)",
                {
                    "param1": img_path,
                    "param2": test_filename,
                    "param3": test_data,
                    "param4": None
                }
            )
            print("   Uspeshno!")
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n3. Variant: Bez ukazaniya imen parametrov (pozicionnye)")
        try:
            # Используем позиционные параметры ?
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(?, ?, ?, ?)",
                [img_path, test_filename, test_data, None]
            )
            print("   Uspeshno!")
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n4. Variant: Proverka sushestvuyushih vyzovov v baze")
        try:
            # Ищем, как вызываются эти процедуры в других местах базы
            result = conn.execute("""
                SELECT FIRST 1 
                    RDB$TRIGGER_SOURCE 
                FROM RDB$TRIGGERS 
                WHERE RDB$TRIGGER_SOURCE LIKE '%wp_SaveBlobToFile%' 
                   OR RDB$TRIGGER_SOURCE LIKE '%wp_DeleteFile%'
            """)
            
            trigger = result.fetchone()
            if trigger and trigger[0]:
                source = trigger[0]
                print(f"   Nayden vyzov v triggere:")
                # Выводим первые 300 символов
                source_preview = source[:300] + "..." if len(source) > 300 else source
                print(f"   {source_preview}")
            else:
                print("   Net vyzovov v triggeryah")
                
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
except Exception as e:
    print(f"Oshibka podklyucheniya: {e}")
    import traceback
    traceback.print_exc()