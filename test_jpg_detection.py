#!/usr/bin/env python
"""
Тест для проверки определения JPG файлов
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routers.image_processing_utils import is_jpg_file

def test_jpg_detection():
    """Тест определения JPG файлов"""
    test_cases = [
        # (имя файла, ожидаемый результат)
        ("test.jpg", True),
        ("test.jpeg", True),
        ("test.JPG", True),
        ("test.JPEG", True),
        ("test.png", False),
        ("test.webp", False),
        ("test.gif", False),
        ("test.bmp", False),
        ("test.jpg?width=100", True),
        ("test.jpeg?height=200", True),
        ("test.jpg?quality=85&width=800", True),
        ("", False),
        (None, False),
    ]
    
    print("Тестирование определения JPG файлов:")
    print("-" * 50)
    
    all_passed = True
    for filename, expected in test_cases:
        if filename is None:
            result = is_jpg_file(None)
        else:
            result = is_jpg_file(filename)
        
        status = "PASS" if result == expected else "FAIL"
        print(f"{status:4} {filename or 'None':30} -> {'JPG' if result else 'не JPG':10} (ожидалось: {'JPG' if expected else 'не JPG'})")
        
        if result != expected:
            all_passed = False
    
    print("-" * 50)
    if all_passed:
        print("Все тесты пройдены успешно!")
    else:
        print("Некоторые тесты не прошли")
    
    return all_passed

def test_real_urls():
    """Тест реальных URL из Ozon и Wildberries"""
    print("\nТестирование реальных URL:")
    print("-" * 50)
    
    real_urls = [
        "https://ozon-st.cdn.ngenix.net/multimedia/1024/123456789.jpg",
        "https://images.wbstatic.net/c516x688/new/123456789.png",
        "https://example.com/image.jpg?width=800&height=600&quality=85",
        "https://example.com/image.webp",
        "https://example.com/image.jpeg?width=1024",
        "https://example.com/image.JPG",
    ]
    
    for url in real_urls:
        filename = url.split('/')[-1].split('?')[0]
        is_jpg = is_jpg_file(filename)
        print(f"{url}")
        print(f"  Файл: {filename}")
        print(f"  JPG: {'ДА' if is_jpg else 'НЕТ'}")
        print()

if __name__ == "__main__":
    test_jpg_detection()
    test_real_urls()