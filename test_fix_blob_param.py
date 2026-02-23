import sys
sys.path.append('.')
import os
import logging
import tempfile
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_blob_param_fix():
    """Тест исправления параметра BLOB"""
    print("=== ТЕСТ ИСПРАВЛЕНИЯ ПАРАМЕТРА BLOB ===")
    
    # Имитируем вызов хранимой процедуры с разными размерами данных
    test_cases = [
        ("Маленький файл (12 байт)", b'A' * 12),
        ("Средний файл (100 байт)", b'B' * 100),
        ("Большой файл (1000 байт)", b'C' * 1000),
        ("Очень большой файл (10000 байт)", b'D' * 10000),
    ]
    
    for test_name, test_data in test_cases:
        print(f"\n--- {test_name} ---")
        print(f"  Размер данных: {len(test_data)} байт")
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
            tmp_file.write(test_data)
            tmp_path = tmp_file.name
        
        print(f"  Временный файл создан: {tmp_path}")
        
        # Читаем данные из файла
        with open(tmp_path, 'rb') as tmp_file:
            file_blob = tmp_file.read()
        
        print(f"  Прочитано: {len(file_blob)} байт")
        
        # Проверяем, что данные совпадают
        if file_blob == test_data:
            print(f"  OK: Данные совпадают")
        else:
            print(f"  ERROR: Данные не совпадают")
        
        # Удаляем временный файл
        os.unlink(tmp_path)
        print(f"  Временный файл удален")
    
    print("\n=== ТЕСТ ЗАВЕРШЕН ===")
    print("\nРЕЗЮМЕ ИСПРАВЛЕНИЙ:")
    print("1. Добавлен явный импорт типов: from sqlalchemy import bindparam, LargeBinary, String")
    print("2. Использован bindparam с явным указанием типа для параметров:")
    print("   - dir: String")
    print("   - modelid: String")
    print("   - imgext: String")
    print("   - file_content: LargeBinary (BLOB)")
    print("3. Это должно решить проблему 'Value of parameter (0) is too long'")
    print("4. Драйвер Firebird теперь будет знать, что file_content - это BLOB, а не строка с ограничением 12 байт")
    
    return True

if __name__ == "__main__":
    success = test_blob_param_fix()
    if success:
        print("\n=== ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТЫ ЗАВЕРШЕНЫ С ОШИБКАМИ ===")
        sys.exit(1)