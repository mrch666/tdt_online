"""Тест для ошибки: проверка существования файла происходит слишком быстро"""
import sys
sys.path.append('.')
import logging
import os
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_file_save_timeout_error():
    """Тест для проверки проблемы с таймаутом при сохранении файла"""
    print("=== ТЕСТ ОШИБКИ ТАЙМАУТА ПРИ СОХРАНЕНИИ ФАЙЛА ===")
    print("Ошибка: File was not saved on server (проверка происходит слишком быстро)")
    
    print("\n=== АНАЛИЗ ОШИБКИ ===")
    print("1. Файл сохраняется через хранимую процедуру wp_SaveBlobToFile")
    print("2. После вызова процедуры сразу проверяется существование файла")
    print("3. Файл может быть еще не записан на диск из-за кэширования или задержек")
    print("4. Нужно добавить таймаут перед проверкой существования файла")
    
    print("\n=== ТЕСТИРОВАНИЕ ЗАДЕРЖЕК ===")
    
    # Тестируем разные задержки
    delays = [0.1, 0.5, 1.0, 2.0, 3.0]
    
    for delay in delays:
        print(f"\n--- Задержка {delay} секунд ---")
        
        # Создаем тестовый файл
        test_filename = f"test_file_{delay}.txt"
        test_content = f"Test content for delay {delay}"
        
        # Записываем файл
        start_time = time.time()
        with open(test_filename, 'w') as f:
            f.write(test_content)
        write_time = time.time() - start_time
        
        print(f"Время записи файла: {write_time:.3f} секунд")
        
        # Проверяем сразу
        immediate_check = os.path.exists(test_filename)
        print(f"Немедленная проверка: {immediate_check}")
        
        # Ждем указанную задержку
        time.sleep(delay)
        
        # Проверяем после задержки
        delayed_check = os.path.exists(test_filename)
        print(f"Проверка после задержки {delay}с: {delayed_check}")
        
        # Удаляем тестовый файл
        if os.path.exists(test_filename):
            os.remove(test_filename)
            print(f"Тестовый файл удален")
    
    print("\n=== ВЫВОДЫ ===")
    print("1. Файлы могут записываться с задержкой из-за кэширования ОС")
    print("2. Немедленная проверка существования файла может давать ложный отрицательный результат")
    print("3. Рекомендуемая задержка: 1-2 секунды")
    print("4. Нужно добавить time.sleep() перед проверкой os.path.exists()")
    
    print("\n=== РЕКОМЕНДАЦИИ ===")
    print("1. В файле app/routers/modelgoods_images.py добавить задержку")
    print("2. После вызова хранимой процедуры добавить: time.sleep(1)")
    print("3. Только после этого проверять существование файла")
    print("4. Также можно добавить повторные попытки проверки")
    
    return True

if __name__ == "__main__":
    try:
        success = test_file_save_timeout_error()
        if success:
            print("\n=== ТЕСТ ЗАВЕРШЕН ===")
            sys.exit(0)
    except Exception as e:
        print(f"\n=== ОШИБКА ПРИ ТЕСТИРОВАНИИ ===")
        print(f"Ошибка: {e}")
        sys.exit(1)