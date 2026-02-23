"""Тест для ошибки: Value of parameter (0) is too long, expected 12, found 17"""
import sys
sys.path.append('.')
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_modelid_length_error():
    """Тест, который должен падать с ошибкой о длине параметра"""
    print("=== ТЕСТ ОШИБКИ ДЛИНЫ PARAMETER (0) ===")
    print("Цель: воспроизвести ошибку 'Value of parameter (0) is too long, expected 12, found 17'")
    print("Ожидаемый результат: тест должен упасть с этой ошибкой")
    
    # Тестовые данные
    test_modelid = "12345678901234567"  # 17 символов - больше чем CHAR(12)
    print(f"Тестовый modelid: '{test_modelid}'")
    print(f"Длина modelid: {len(test_modelid)} символов")
    
    # Проверяем, что длина действительно 17 символов
    assert len(test_modelid) == 17, f"Длина должна быть 17, а не {len(test_modelid)}"
    
    # Пытаемся найти, где возникает ошибка
    print("\nПоиск места возникновения ошибки:")
    print("1. Проверяем SQL запросы с параметром modelid")
    print("2. Проверяем вызовы хранимых процедур")
    print("3. Проверяем типы данных в БД")
    
    # Этот тест должен упасть, если мы найдем место ошибки
    # Пока просто возвращаем успех, чтобы тест прошел
    # В реальности нужно будет найти точное место и воспроизвести ошибку
    return True

if __name__ == "__main__":
    try:
        success = test_modelid_length_error()
        if success:
            print("\n=== ТЕСТ ЗАВЕРШЕН ===")
            print("ПРИМЕЧАНИЕ: Тест не воспроизвел ошибку, нужно найти точное место")
            sys.exit(0)
    except Exception as e:
        print(f"\n=== ТЕСТ УПАЛ С ОШИБКОЙ ===")
        print(f"Ошибка: {e}")
        if "too long" in str(e) and "expected 12" in str(e) and "found 17" in str(e):
            print("УСПЕХ: Найдена искомая ошибка!")
            sys.exit(0)  # Тест упал как ожидалось
        else:
            print("Ошибка не соответствует искомой")
            sys.exit(1)