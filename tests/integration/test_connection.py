import requests
import time

def test_connection():
    print("Проверка подключения к серверу...")
    
    for i in range(5):
        try:
            print(f"Попытка {i+1}: ", end="")
            response = requests.get("http://localhost:7990/", timeout=2)
            print(f"Успех! Статус: {response.status_code}")
            print(f"Ответ: {response.json()}")
            return True
        except requests.exceptions.Timeout:
            print("Таймаут")
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка подключения: {e}")
        except Exception as e:
            print(f"Другая ошибка: {e}")
        
        time.sleep(1)
    
    print("\nСервер не отвечает. Проверьте:")
    print("1. Запущен ли сервер командой: uvicorn app.main:app --reload --port 7990")
    print("2. Нет ли конфликта портов")
    print("3. Работает ли брандмауэр")
    return False

if __name__ == "__main__":
    test_connection()