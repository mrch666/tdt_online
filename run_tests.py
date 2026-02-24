#!/usr/bin/env python
"""
Скрипт для запуска всех тестов проекта.
Используется для общего тестирования после перемещения тестов в папку tests/
"""

import subprocess
import sys
import os

def run_tests():
    """Запуск всех тестов в папке tests/"""
    print("=" * 60)
    print("Запуск всех тестов проекта")
    print("=" * 60)
    
    # Команда для запуска pytest
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    
    print(f"Команда: {' '.join(cmd)}")
    print()
    
    try:
        # Запускаем тесты
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        
        # Выводим результат
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print("=" * 60)
        print(f"Код завершения: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Все тесты прошли успешно!")
        else:
            print("❌ Некоторые тесты не прошли")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Ошибка при запуске тестов: {e}")
        return 1

def run_specific_tests():
    """Запуск основных тестов (без интеграционных)"""
    print("=" * 60)
    print("Запуск основных тестов")
    print("=" * 60)
    
    # Запускаем только основные тесты
    test_files = [
        "tests/test_main.py",
        "tests/test_modelgoods_parameters.py",
        "tests/test_external_images_port_error.py",
        "tests/test_external_images_port_fixed.py",
        "tests/test_external_images_identity_key_simple.py",
        "tests/test_port_configuration.py",
        "tests/test_tempfile_cleanup.py"
    ]
    
    cmd = [sys.executable, "-m", "pytest"] + test_files + ["-v", "--tb=short"]
    
    print(f"Команда: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print("=" * 60)
        print(f"Код завершения: {result.returncode}")
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Ошибка при запуске тестов: {e}")
        return 1

if __name__ == "__main__":
    # По умолчанию запускаем все тесты
    if len(sys.argv) > 1 and sys.argv[1] == "--basic":
        exit_code = run_specific_tests()
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)