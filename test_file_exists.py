import sys
sys.path.append('.')
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def test_file_exists():
    """Тест проверки существования файла после сохранения"""
    print("=== Тест проверки существования файла ===")
    
    modelid = "000001002Qa{"
    imgext = "gif"
    
    try:
        # Получаем путь к каталогу с изображениями
        img_path = os.path.join(os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases'), 
                               os.getenv('IMG_SUBDIR', 'img')) + os.sep
        
        # Формируем имя файла как это делает приложение
        # В реальном приложении используется DEC64I0 и DEC64I1 из БД
        # Для теста используем известные значения
        filename = f"1_633150.{imgext}"
        full_path = os.path.join(img_path, filename)
        
        print(f"Проверяем файл:")
        print(f"  - Путь к каталогу: {img_path}")
        print(f"  - Имя файла: {filename}")
        print(f"  - Полный путь: {full_path}")
        print(f"  - Каталог существует: {os.path.exists(img_path)}")
        
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"\nФАЙЛ СУЩЕСТВУЕТ!")
            print(f"  - Размер файла: {file_size} байт")
            print(f"  - Время изменения: {os.path.getmtime(full_path)}")
            
            # Пробуем прочитать файл
            try:
                with open(full_path, 'rb') as f:
                    file_data = f.read()
                print(f"  - Успешно прочитано: {len(file_data)} байт")
                print(f"  - Первые 20 байт: {file_data[:20]}")
                
                # Проверяем, что это GIF
                if file_data.startswith(b'GIF'):
                    print(f"  - Это GIF файл (валидный заголовок)")
                else:
                    print(f"  - Внимание: не GIF заголовок")
                    
            except Exception as e:
                print(f"  - Ошибка при чтении файла: {e}")
                
            # Проверяем права доступа
            print(f"\nПроверка прав доступа:")
            try:
                # Пробуем создать тестовый файл
                test_file = os.path.join(img_path, "test_access.tmp")
                with open(test_file, 'wb') as f:
                    f.write(b'test')
                print(f"  - Права на запись: ЕСТЬ")
                
                # Пробуем удалить тестовый файл
                os.remove(test_file)
                print(f"  - Права на удаление: ЕСТЬ")
                
            except PermissionError as e:
                print(f"  - Права на запись/удаление: НЕТ ({e})")
            except Exception as e:
                print(f"  - Ошибка при проверке прав: {e}")
                
        else:
            print(f"\nФАЙЛ НЕ СУЩЕСТВУЕТ!")
            print(f"  - Проверьте работу хранимой процедуры wp_SaveBlobToFile")
            print(f"  - Проверьте права доступа службы Firebird к каталогу")
            print(f"  - Проверьте путь: {full_path}")
            
            # Проверяем, есть ли другие файлы в каталоге
            print(f"\nСодержимое каталога {img_path}:")
            try:
                files = os.listdir(img_path)
                print(f"  - Всего файлов: {len(files)}")
                if files:
                    print(f"  - Первые 10 файлов: {files[:10]}")
                    
                    # Ищем файлы с похожими именами
                    similar_files = [f for f in files if f.startswith('1_')]
                    print(f"  - Файлы начинающиеся с '1_': {similar_files}")
            except Exception as e:
                print(f"  - Ошибка при чтении каталога: {e}")
        
        return os.path.exists(full_path)
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    exists = test_file_exists()
    if exists:
        print("\n=== ТЕСТ ЗАВЕРШЕН: ФАЙЛ СУЩЕСТВУЕТ ===")
        sys.exit(0)
    else:
        print("\n=== ТЕСТ ЗАВЕРШЕН: ФАЙЛ НЕ НАЙДЕН ===")
        sys.exit(1)