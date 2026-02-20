import sys
sys.path.append('.')
from app.database import engine

try:
    with engine.connect() as conn:
        # Ищем процедуры с префиксом WP_
        print("Procedury s prefiksom WP_:")
        result = conn.execute("SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES WHERE RDB$PROCEDURE_NAME LIKE 'WP_%'")
        wp_procs = result.fetchall()
        
        if wp_procs:
            for p in wp_procs:
                proc_name = p[0].strip() if p[0] else ''
                print(f"  - {proc_name}")
        else:
            print("  Net procedur s prefiksom WP_")
            
        # Ищем процедуры связанные с файлами
        print("\nProcedury svyazannye s failami (FILE, BLOB, SAVE):")
        result = conn.execute("SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES WHERE RDB$PROCEDURE_NAME LIKE '%FILE%' OR RDB$PROCEDURE_NAME LIKE '%BLOB%' OR RDB$PROCEDURE_NAME LIKE '%SAVE%'")
        file_procs = result.fetchall()
        
        if file_procs:
            for p in file_procs:
                proc_name = p[0].strip() if p[0] else ''
                print(f"  - {proc_name}")
        else:
            print("  Net procedur svyazannyh s failami")
            
        # Проверяем процедуру wp_DeleteFile которая используется в коде
        print("\nProverka procedury wp_DeleteFile:")
        result = conn.execute("SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES WHERE RDB$PROCEDURE_NAME = 'wp_DeleteFile'")
        delete_proc = result.fetchone()
        if delete_proc:
            print(f"  OK: Procedura wp_DeleteFile naydena: {delete_proc[0]}")
        else:
            print("  ERROR: Procedura wp_DeleteFile NE naydena")
            
except Exception as e:
    print(f"Oshibka: {e}")
    import traceback
    traceback.print_exc()