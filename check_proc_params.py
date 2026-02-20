import sys
sys.path.append('.')
from app.database import engine

try:
    with engine.connect() as conn:
        print("1. Parametry procedury wp_SaveBlobToFile:")
        
        # Получаем информацию о параметрах процедуры
        result = conn.execute("""
            SELECT 
                RDB$PARAMETER_NAME,
                RDB$PARAMETER_TYPE,
                RDB$FIELD_SOURCE
            FROM RDB$PROCEDURE_PARAMETERS 
            WHERE RDB$PROCEDURE_NAME = 'wp_SaveBlobToFile'
            ORDER BY RDB$PARAMETER_NUMBER
        """)
        
        params = result.fetchall()
        if params:
            for p in params:
                param_name = p[0].strip() if p[0] else ''
                param_type = 'INPUT' if p[1] == 0 else 'OUTPUT'
                field_source = p[2].strip() if p[2] else ''
                print(f"   - {param_name} ({param_type}), type: {field_source}")
        else:
            print("   Net informacii o parametrah")
            
        print("\n2. Parametry procedury wp_DeleteFile:")
        result = conn.execute("""
            SELECT 
                RDB$PARAMETER_NAME,
                RDB$PARAMETER_TYPE,
                RDB$FIELD_SOURCE
            FROM RDB$PROCEDURE_PARAMETERS 
            WHERE RDB$PROCEDURE_NAME = 'wp_DeleteFile'
            ORDER BY RDB$PARAMETER_NUMBER
        """)
        
        params = result.fetchall()
        if params:
            for p in params:
                param_name = p[0].strip() if p[0] else ''
                param_type = 'INPUT' if p[1] == 0 else 'OUTPUT'
                field_source = p[2].strip() if p[2] else ''
                print(f"   - {param_name} ({param_type}), type: {field_source}")
        else:
            print("   Net informacii o parametrah")
            
        # Проверяем, как вызываются процедуры в других местах
        print("\n3. Proverka sushestvuyushih vyzovov procedur:")
        
        # Ищем вызовы процедур в коде базы (триггеры, другие процедуры)
        result = conn.execute("""
            SELECT FIRST 5 
                RDB$PROCEDURE_SOURCE 
            FROM RDB$PROCEDURES 
            WHERE RDB$PROCEDURE_SOURCE LIKE '%wp_SaveBlobToFile%' 
               OR RDB$PROCEDURE_SOURCE LIKE '%wp_DeleteFile%'
        """)
        
        procs_with_calls = result.fetchall()
        if procs_with_calls:
            print("   Naydeny vyzovy v drugih procedurah:")
            for i, proc in enumerate(procs_with_calls):
                source = proc[0]
                if source:
                    source_str = source[:200] + "..." if len(source) > 200 else source
                    print(f"   {i+1}. {source_str}")
        else:
            print("   Net vyzovov v drugih procedurah")
            
except Exception as e:
    print(f"Oshibka: {e}")
    import traceback
    traceback.print_exc()