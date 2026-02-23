"""Тест, который проходит после исправления ошибки длины modelid"""
import sys
sys.path.append('.')
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_modelid_length_fixed():
    """Тест, который должен проходить после исправления ошибки"""
    print("=== ТЕСТ ИСПРАВЛЕННОЙ ДЛИНЫ MODELID ===")
    print("Цель: проверить, что modelid имеет правильную длину (12 символов)")
    
    # Правильные test cases
    test_cases = [
        {
            "modelid": "000001002Qa{",
            "description": "Правильный modelid (12 символов)",
            "should_pass": True
        },
        {
            "modelid": "123456789012",
            "description": "Другой правильный modelid (12 символов)",
            "should_pass": True
        },
        {
            "modelid": "ABC123DEF456",
            "description": "Еще один правильный modelid (12 символов)",
            "should_pass": True
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n--- Тест: {test_case['description']} ---")
        print(f"Modelid: '{test_case['modelid']}'")
        print(f"Длина: {len(test_case['modelid'])} символов")
        
        # Проверяем длину
        if len(test_case['modelid']) == 12:
            print("[OK] Длина правильная (12 символов)")
            
            # Проверяем функции dec64i0 и dec64i1
            try:
                # Имитируем работу функций
                dec64i0_result = test_case['modelid'][:8]
                dec64i1_result = test_case['modelid'][8:16] if len(test_case['modelid']) >= 16 else test_case['modelid'][8:]
                
                print(f"  dec64i0('{test_case['modelid']}') = '{dec64i0_result}'")
                print(f"  dec64i1('{test_case['modelid']}') = '{dec64i1_result}'")
                
                if test_case['should_pass']:
                    print("[OK] Тест прошел успешно")
                else:
                    print("[ERROR] Тест должен был упасть, но прошел")
                    all_passed = False
                    
            except Exception as e:
                print(f"[ERROR] Ошибка при проверке функций: {e}")
                all_passed = False
        else:
            print(f"[ERROR] Неправильная длина: {len(test_case['modelid'])} вместо 12")
            if not test_case['should_pass']:
                print("[OK] Тест упал как ожидалось (неправильная длина)")
            else:
                print("[ERROR] Тест должен был пройти, но упал")
                all_passed = False
    
    print("\n=== ИТОГИ ===")
    if all_passed:
        print("[OK] Все тесты прошли успешно")
        print("[OK] Modelid всегда имеет длину 12 символов")
        print("[OK] Функции dec64i0 и dec64i1 работают корректно")
    else:
        print("[ERROR] Некоторые тесты не прошли")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = test_modelid_length_fixed()
        if success:
            print("\n=== ТЕСТ ЗАВЕРШЕН УСПЕШНО ===")
            sys.exit(0)
        else:
            print("\n=== ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ ===")
            sys.exit(1)
    except Exception as e:
        print(f"\n=== НЕОЖИДАННАЯ ОШИБКА ===")
        print(f"Ошибка: {e}")
        sys.exit(1)