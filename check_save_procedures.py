import sys
sys.path.append('.')
from app.database import engine

try:
    with engine.connect() as conn:
        print("1. Proverka procedury 'wp_saveblobtofile' (nizhnij registr):")
        result = conn.execute("SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES WHERE RDB$PROCEDURE_NAME = 'wp_saveblobtofile'")
        proc = result.fetchone()
        if proc:
            print(f"   OK: {proc[0]}")
        else:
            print("   ERROR: Ne naydena")
            
        print("\n2. Proverka bez ucheta registra (WP_SAVEBLOBTOFILE):")
        result = conn.execute("SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES WHERE UPPER(RDB$PROCEDURE_NAME) = 'WP_SAVEBLOBTOFILE'")
        proc = result.fetchone()
        if proc:
            print(f"   OK: {proc[0]}")
        else:
            print("   ERROR: Ne naydena")
            
        print("\n3. Vse procedury s 'save' v nazvanii:")
        result = conn.execute("SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES WHERE RDB$PROCEDURE_NAME LIKE '%SAVE%' OR RDB$PROCEDURE_NAME LIKE '%save%'")
        save_procs = result.fetchall()
        if save_procs:
            for p in save_procs:
                proc_name = p[0].strip() if p[0] else ''
                print(f"   - {proc_name}")
        else:
            print("   Net takih procedur")
            
        print("\n4. Vse procedury s 'blob' v nazvanii:")
        result = conn.execute("SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES WHERE RDB$PROCEDURE_NAME LIKE '%BLOB%' OR RDB$PROCEDURE_NAME LIKE '%blob%'")
        blob_procs = result.fetchall()
        if blob_procs:
            for p in blob_procs:
                proc_name = p[0].strip() if p[0] else ''
                print(f"   - {proc_name}")
        else:
            print("   Net takih procedur")
            
        print("\n5. Vse procedury s 'file' v nazvanii:")
        result = conn.execute("SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES WHERE RDB$PROCEDURE_NAME LIKE '%FILE%' OR RDB$PROCEDURE_NAME LIKE '%file%'")
        file_procs = result.fetchall()
        if file_procs:
            for p in file_procs:
                proc_name = p[0].strip() if p[0] else ''
                print(f"   - {proc_name}")
        else:
            print("   Net takih procedur")
            
except Exception as e:
    print(f"Oshibka: {e}")
    import traceback
    traceback.print_exc()