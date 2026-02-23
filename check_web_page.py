import requests
import sys

def check_web_page():
    """Проверяет доступность веб-страницы через localhost"""
    try:
        print("Проверка доступности http://localhost:7990/web/external-images/")
        response = requests.get('http://localhost:7990/web/external-images/', timeout=5)
        
        print(f"Статус: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Длина ответа: {len(response.text)} символов")
        
        if response.status_code == 200:
            print("✓ Страница доступна через localhost:7990")
            
            # Проверяем основные элементы
            html_content = response.text
            checks = [
                ("Заголовок 'Внешние изображения товаров'", 
                 'Внешние изображения товаров' in html_content),
                ("Чекбокс 'Показать скрытые товары'", 
                 'Показать скрытые товары' in html_content),
                ("Карточки товаров", 
                 'product-card' in html_content),
                ("Изображения", 
                 'img-thumbnail' in html_content or 'thumbnail' in html_content),
                ("Кнопки обработки", 
                 'process-image' in html_content or 'btn-process' in html_content)
            ]
            
            print("\nПроверка элементов на странице:")
            for check_name, check_result in checks:
                status = "✓" if check_result else "✗"
                print(f"  {status} {check_name}")
            
            return True
        else:
            print(f"✗ Ошибка: HTTP {response.status_code}")
            print(f"Текст ответа (первые 500 символов):")
            print(response.text[:500])
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Не удалось подключиться к localhost:7990")
        print("Возможные причины:")
        print("  1. Приложение не запущено")
        print("  2. Приложение запущено на другом порту")
        print("  3. Брандмауэр блокирует подключение")
        return False
    except Exception as e:
        print(f"✗ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_web_page()
    sys.exit(0 if success else 1)