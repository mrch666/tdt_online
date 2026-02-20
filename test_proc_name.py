import sys
sys.path.append('.')
from app.database import engine

try:
    with engine.connect() as conn:
        # Получаем точное название процедуры
        result = conn.execute("SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES WHERE UPPER(RDB$PROCEDURE_NAME) = 'WP_SAVEBLOBTOFILE'")
        proc = result.fetchone()
        if proc:
            exact_name = proc[0]
            if exact_name:
                exact_name = exact_name.strip()
            
            print(f"Tochnoe nazvanie procedury iz bazy: '{exact_name}'")
            print(f"Dlina nazvaniya: {len(exact_name)}")
            
            # Проверяем совпадение с тем, что в коде
            code_name = "wp_SaveBlobToFile"
            print(f"\nNazvanie v kode: '{code_name}'")
            print(f"Dlina v kode: {len(code_name)}")
            
            if exact_name == code_name:
                print("SOVPADAET! Problema ne v nazvanii.")
            else:
                print("NE SOVPADAET! Vot v chem razlichie:")
                print(f"  Baza:  '{exact_name}'")
                print(f"  Kod:   '{code_name}'")
                
                # Проверяем посимвольно
                print("\nPosimvolnoe sravnenie:")
                for i in range(max(len(exact_name), len(code_name))):
                    char1 = exact_name[i] if i < len(exact_name) else ' '
                    char2 = code_name[i] if i < len(code_name) else ' '
                    print(f"  Pozitsiya {i:2}: baza='{char1}' (kod={ord(char1):3}), kod='{char2}' (kod={ord(char2):3}) - {'SOVPADAET' if char1 == char2 else 'RAZLICHIE'}")
        else:
            print("Procedura ne naydena v baze!")
            
except Exception as e:
    print(f"Oshibka: {e}")
    import traceback
    traceback.print_exc()