import sys
sys.path.append('.')
from app.database import engine
import os

try:
    with engine.connect() as conn:
        # Тестовые данные
        test_path = "C:\\Program Files (x86)\\tdt3\\bases\\img"
        test_filename = "test_image.jpg"
        test_data = b"test image data"
        
        print(f"Testovye dannye:")
        print(f"  Put: {test_path}")
        print(f"  Imya faila: {test_filename}")
        print(f"  Dannye: {len(test_data)} bayt")
        
        # Пробуем вызвать процедуру
        print(f"\nPytaemsya vyzvat proceduru wp_SaveBlobToFile...")
        try:
            result = conn.execute(
                "SELECT * FROM \"wp_SaveBlobToFile\"(:path, :filename, :data)",
                {"path": test_path, "filename": test_filename, "data": test_data}
            )
            print("Procedura uspeshno vyzvana!")
            
            # Пробуем получить результат
            row = result.fetchone()
            if row:
                print(f"Rezultat: {row}")
            else:
                print("Procedura vernula pustoj rezultat")
                
        except Exception as e:
            print(f"OSHIBKA pri vyzove procedury: {e}")
            import traceback
            traceback.print_exc()
            
        # Проверяем процедуру wp_DeleteFile
        print(f"\n\nProverka procedury wp_DeleteFile...")
        try:
            result = conn.execute(
                "SELECT * FROM \"wp_DeleteFile\"(:path, :filename)",
                {"path": test_path, "filename": test_filename}
            )
            print("Procedura wp_DeleteFile uspeshno vyzvana!")
            
            row = result.fetchone()
            if row:
                print(f"Rezultat: {row}")
            else:
                print("Procedura vernula pustoj rezultat")
                
        except Exception as e:
            print(f"OSHIBKA pri vyzove wp_DeleteFile: {e}")
            
except Exception as e:
    print(f"Oshibka podklyucheniya: {e}")
    import traceback
    traceback.print_exc()