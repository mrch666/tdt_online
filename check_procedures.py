import sys
import os
sys.path.append('.')

from app.database import engine

try:
    with engine.connect() as conn:
        # Проверяем существование процедуры WP_SAVEBLOBTOFILE
        print("Proverka procedury WP_SAVEBLOBTOFILE...")
        result = conn.execute("SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES WHERE RDB$PROCEDURE_NAME = 'WP_SAVEBLOBTOFILE'")
        proc = result.fetchone()
        if proc:
            print(f"OK: Procedura WP_SAVEBLOBTOFILE naydena: {proc[0]}")
        else:
            print("ERROR: Procedura WP_SAVEBLOBTOFILE NE naydena v baze dannyh")
        
        # Проверяем альтернативные варианты
        print("\nPoisk pohozhih procedur...")
        result = conn.execute("SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES WHERE RDB$PROCEDURE_NAME LIKE '%SAVE%' OR RDB$PROCEDURE_NAME LIKE '%BLOB%' OR RDB$PROCEDURE_NAME LIKE '%FILE%'")
        procs = result.fetchall()
        
        if procs:
            print("Naydeny procedury:")
            for p in procs:
                proc_name = p[0].strip() if p[0] else ""
                print(f"  - {proc_name}")
        else:
            print("Pohozhih procedur ne naydeno")
            
        # Проверяем все процедуры
        print("\nVse procedury v baze dannyh:")
        result = conn.execute("SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES ORDER BY RDB$PROCEDURE_NAME")
        all_procs = result.fetchall()
        for p in all_procs[:20]:  # Покажем первые 20
            proc_name = p[0].strip() if p[0] else ""
            print(f"  - {proc_name}")
        
        if len(all_procs) > 20:
            print(f"  ... i eshe {len(all_procs) - 20} procedur")
            
except Exception as e:
    print(f"Oshibka podklyucheniya: {e}")
    import traceback
    traceback.print_exc()
