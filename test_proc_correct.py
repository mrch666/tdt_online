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
        print(f"  BASE_DIR: {base_dir}")
        print(f"  IMG_SUBDIR: {img_subdir}")
        print(f"  img_path (papka): {img_path}")
        print(f"  test_filename: {test_filename}")
        print(f"  full_path (papka + file): {full_path}")
        print(f"  Dannye: {len(test_data)} bayt")
        
        # Пробуем разные варианты вызова процедуры
        print(f"\n1. Variant 1: iPathDB = put' k baze, iPath = polnyj put' k failu")
        try:
            # Возможно, iPathDB - это путь к базе данных
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(:iPathDB, :oRes, :iPath, :iBlob)",
                {
                    "iPathDB": base_dir,  # Путь к базе данных
                    "oRes": None,  # Выходной параметр
                    "iPath": full_path,  # Полный путь к файлу
                    "iBlob": test_data  # Данные файла
                }
            )
            print("   Uspeshno!")
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n2. Variant 2: iPathDB = put' k papke s izobrazheniyami, iPath = imya faila")
        try:
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(:iPathDB, :oRes, :iPath, :iBlob)",
                {
                    "iPathDB": img_path,  # Путь к папке с изображениями
                    "oRes": None,  # Выходной параметр
                    "iPath": test_filename,  # Имя файла
                    "iBlob": test_data  # Данные файла
                }
            )
            print("   Uspeshno!")
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        print(f"\n3. Variant 3: Tol'ko obyazatel'nye parametry (bez oRes)")
        try:
            # Может быть, oRes - выходной параметр, и его не нужно передавать при вызове
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(:iPathDB, :iPath, :iBlob)",
                {
                    "iPathDB": img_path,
                    "iPath": test_filename,
                    "iBlob": test_data
                }
            )
            print("   Uspeshno!")
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
        # Проверяем процедуру удаления
        print(f"\n4. Procedura wp_DeleteFile:")
        try:
            result = conn.execute(
                "SELECT * FROM \"wp_DeleteFile\"(:iPathDB, :oRes, :iPath)",
                {
                    "iPathDB": img_path,
                    "oRes": None,
                    "iPath": test_filename
                }
            )
            print("   Uspeshno!")
            row = result.fetchone()
            if row:
                print(f"   Rezultat: {row}")
        except Exception as e:
            print(f"   OSHIBKA: {e}")
            
except Exception as e:
    print(f"Oshibka podklyucheniya: {e}")
    import traceback
    traceback.print_exc()