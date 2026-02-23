"""Поиск точного места ошибки: Value of parameter (0) is too long, expected 12, found 17"""
import sys
sys.path.append('.')
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_find_error_location():
    """Поиск точного места возникновения ошибки"""
    print("=== ПОИСК ТОЧНОГО МЕСТА ОШИБКИ ===")
    print("Ошибка: 'Value of parameter (0) is too long, expected 12, found 17'")
    print("\nАнализ:")
    print("1. Параметр (0) - это первый параметр в SQL запросе")
    print("2. Ожидается 12 символов, передается 17")
    print("3. Это может быть параметр типа CHAR(12) или VARCHAR(12)")
    
    print("\n=== ПРОВЕРКА ВОЗМОЖНЫХ МЕСТ ===")
    
    # Проверяем разные места в коде
    test_cases = [
        {
            "name": "Проверка modelid в таблице modelgoods",
            "description": "Поле id имеет тип CHAR(12)",
            "test_value": "12345678901234567",  # 17 символов
            "expected_error": True
        },
        {
            "name": "Проверка параметра iPathDB в wp_SaveBlobToFile",
            "description": "Параметр iPathDB имеет тип char(400) - не должен давать ошибку 12 символов",
            "test_value": "C:\\Program Files (x86)\\tdt3\\bases\\img",
            "expected_error": False
        },
        {
            "name": "Проверка параметра iPath в wp_SaveBlobToFile",
            "description": "Параметр iPath имеет тип char(100) - не должен давать ошибку 12 символов",
            "test_value": "test_filename.jpg",
            "expected_error": False
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        print(f"Описание: {test_case['description']}")
        print(f"Тестовое значение: '{test_case['test_value']}'")
        print(f"Длина: {len(test_case['test_value'])} символов")
        
        if len(test_case['test_value']) == 17:
            print("[WARNING] Длина 17 символов - соответствует ошибке!")
        
        if test_case['expected_error']:
            print("Ожидается ошибка: ДА")
        else:
            print("Ожидается ошибка: НЕТ")
    
    print("\n=== ВЫВОДЫ ===")
    print("1. Ошибка скорее всего связана с полем modelid (CHAR(12))")
    print("2. Где-то передается строка длиной 17 символов вместо 12")
    print("3. Нужно проверить все SQL запросы с параметром :modelid")
    print("4. Особое внимание - вызовы функций dec64i0() и dec64i1()")
    
    print("\n=== РЕКОМЕНДАЦИИ ===")
    print("1. Добавить логирование длины modelid перед каждым SQL запросом")
    print("2. Проверить, что modelid всегда имеет длину 12 символов")
    print("3. Проверить работу функций dec64i0() и dec64i1()")
    
    return True

if __name__ == "__main__":
    try:
        success = test_find_error_location()
        if success:
            print("\n=== АНАЛИЗ ЗАВЕРШЕН ===")
            sys.exit(0)
    except Exception as e:
        print(f"\n=== ОШИБКА ПРИ АНАЛИЗЕ ===")
        print(f"Ошибка: {e}")
        sys.exit(1)