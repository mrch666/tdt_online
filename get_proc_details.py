import sys
sys.path.append('.')
from app.database import engine

try:
    with engine.connect() as conn:
        print("=== Polnaya informaciya o procedurah ===")
        
        # Получаем информацию о процедуре wp_SaveBlobToFile
        print("\n1. Procedura wp_SaveBlobToFile:")
        
        # Получаем исходный код процедуры
        result = conn.execute("""
            SELECT 
                RDB$PROCEDURE_SOURCE
            FROM RDB$PROCEDURES 
            WHERE RDB$PROCEDURE_NAME = 'wp_SaveBlobToFile'
        """)
        
        proc_source = result.fetchone()
        if proc_source and proc_source[0]:
            source = proc_source[0]
            print(f"   Istochnyj kod (pervye 500 simvolov):")
            print(f"   {source[:500]}...")
        else:
            print("   Net istochnogo koda")
            
        # Получаем информацию о типах параметров
        print("\n2. Tipy parametrov procedury wp_SaveBlobToFile:")
        result = conn.execute("""
            SELECT 
                pp.RDB$PARAMETER_NAME,
                pp.RDB$PARAMETER_TYPE,
                f.RDB$FIELD_TYPE,
                f.RDB$FIELD_SUB_TYPE,
                f.RDB$FIELD_LENGTH,
                f.RDB$FIELD_SCALE
            FROM RDB$PROCEDURE_PARAMETERS pp
            LEFT JOIN RDB$FIELDS f ON pp.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
            WHERE pp.RDB$PROCEDURE_NAME = 'wp_SaveBlobToFile'
            ORDER BY pp.RDB$PARAMETER_NUMBER
        """)
        
        params = result.fetchall()
        if params:
            for p in params:
                param_name = p[0].strip() if p[0] else ''
                param_type = 'INPUT' if p[1] == 0 else 'OUTPUT'
                field_type = p[2]
                sub_type = p[3]
                length = p[4]
                scale = p[5]
                
                # Преобразуем тип поля
                type_map = {
                    7: 'SMALLINT',
                    8: 'INTEGER',
                    10: 'FLOAT',
                    12: 'DATE',
                    13: 'TIME',
                    14: 'CHAR',
                    16: 'BIGINT',
                    27: 'DOUBLE',
                    35: 'TIMESTAMP',
                    37: 'VARCHAR',
                    261: 'BLOB'
                }
                
                field_type_str = type_map.get(field_type, f'UNKNOWN({field_type})')
                
                # Для BLOB определяем подтип
                if field_type == 261:
                    if sub_type == 0:
                        field_type_str = 'BLOB SUB_TYPE 0 (binary)'
                    elif sub_type == 1:
                        field_type_str = 'BLOB SUB_TYPE 1 (text)'
                    else:
                        field_type_str = f'BLOB SUB_TYPE {sub_type}'
                
                print(f"   - {param_name} ({param_type}): {field_type_str}, dlina: {length}, scale: {scale}")
        else:
            print("   Net informacii o parametrah")
            
        print("\n3. Procedura wp_DeleteFile:")
        result = conn.execute("""
            SELECT 
                pp.RDB$PARAMETER_NAME,
                pp.RDB$PARAMETER_TYPE,
                f.RDB$FIELD_TYPE,
                f.RDB$FIELD_SUB_TYPE,
                f.RDB$FIELD_LENGTH,
                f.RDB$FIELD_SCALE
            FROM RDB$PROCEDURE_PARAMETERS pp
            LEFT JOIN RDB$FIELDS f ON pp.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
            WHERE pp.RDB$PROCEDURE_NAME = 'wp_DeleteFile'
            ORDER BY pp.RDB$PARAMETER_NUMBER
        """)
        
        params = result.fetchall()
        if params:
            for p in params:
                param_name = p[0].strip() if p[0] else ''
                param_type = 'INPUT' if p[1] == 0 else 'OUTPUT'
                field_type = p[2]
                sub_type = p[3]
                length = p[4]
                scale = p[5]
                
                field_type_str = 'UNKNOWN'
                if field_type == 37:
                    field_type_str = 'VARCHAR'
                elif field_type == 14:
                    field_type_str = 'CHAR'
                elif field_type == 8:
                    field_type_str = 'INTEGER'
                
                print(f"   - {param_name} ({param_type}): {field_type_str}, dlina: {length}, scale: {scale}")
        else:
            print("   Net informacii o parametrah")
            
except Exception as e:
    print(f"Oshibka: {e}")
    import traceback
    traceback.print_exc()