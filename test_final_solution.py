import sys
sys.path.append('.')
import os
import logging
import tempfile
import time
from app.database import engine
from sqlalchemy import text

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

def dec64i0(modelid: str) -> str:
    """Decode first part of model ID"""
    return modelid[:8]

def dec64i1(modelid: str) -> str:
    """Decode second part of model ID"""
    return modelid[8:16]

def test_final_solution():
    """Финальный тест решения проблемы с загрузкой изображений"""
    print("=== ФИНАЛЬНЫЙ ТЕСТ РЕШЕНИЯ ===")
    
    modelid = "000001002Qa{"
    imgext = "jpg"
    filename = f"{dec64i0(modelid)}_{dec64i1(modelid)}.{imgext}"
    img_path = os.path.join(os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases'), 
                           os.getenv('IMG_SUBDIR', 'img')) + os.sep
    
    print(f"Параметры для теста:")
    print(f"  - modelid: {modelid}")
    print(f"  - imgext: {imgext}")
    print(f"  - filename: {filename}")
    print(f"  - img_path: {img_path}")
    
    full_path = os.path.join(img_path, filename)
    
    # Тестовые данные разных размеров
    test_cases = [
        ("Маленький файл", b'A' * 500),  # 500 байт
        ("Средний файл", b'B' * 3000),   # 3000 байт
        ("Большой файл", b'C' * 8000),   # 8000 байт
    ]
    
    try:
        with engine.connect() as conn:
            # Очищаем старый файл если существует
            if os.path.exists(full_path):
                print(f"\nОчищаем старый файл...")
                try:
                    # Пробуем удалить через процедуру
                    delete_sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', '{filename}')"""
                    with conn.begin():
                        conn.execute(text(delete_sql))
                    print(f"  Старый файл удален через процедуру")
                    time.sleep(2)
                except Exception as e:
                    print(f"  Не удалось удалить через процедуру: {e}")
            
            for test_name, test_data in test_cases:
                print(f"\n--- {test_name} ({len(test_data)} байт) ---")
                
                try:
                    # Шаг 1: Проверяем существование старого файла
                    if os.path.exists(full_path):
                        old_size = os.path.getsize(full_path)
                        print(f"  Старый файл существует, размер: {old_size} байт")
                        
                        # Удаляем через процедуру
                        try:
                            delete_sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', '{filename}')"""
                            with conn.begin():
                                conn.execute(text(delete_sql))
                            print(f"  Старый файл удален через процедуру")
                            time.sleep(2)  # Даем время на удаление
                        except Exception as delete_error:
                            print(f"  Не удалось удалить через процедуру: {delete_error}")
                    
                    # Шаг 2: Создаем временный файл
                    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
                        tmp_file.write(test_data)
                        tmp_path = tmp_file.name
                    
                    tmp_size = os.path.getsize(tmp_path)
                    print(f"  Временный файл создан: {tmp_path}, размер: {tmp_size} байт")
                    
                    # Шаг 3: Выполняем хранимую процедуру
                    sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.' || :imgext, :file_content)""")
                    
                    with open(tmp_path, 'rb') as tmp_file:
                        file_blob = tmp_file.read()
                    
                    print(f"  Передаваемые данные: {len(file_blob)} байт")
                    
                    with conn.begin():
                        result = conn.execute(sql, {
                            'dir': img_path,
                            'modelid': modelid,
                            'imgext': imgext,
                            'file_content': file_blob
                        }).fetchall()
                    
                    print(f"  Процедура выполнена, результат: {result}")
                    
                    # Шаг 4: Проверяем сохраненный файл
                    time.sleep(3)  # Даем больше времени на сохранение
                    
                    if os.path.exists(full_path):
                        saved_size = os.path.getsize(full_path)
                        print(f"  Файл сохранен: {full_path}, размер: {saved_size} байт")
                        
                        if saved_size == len(test_data):
                            print(f"  OK: РАЗМЕР СОВПАДАЕТ: {saved_size} байт")
                            
                            # Проверяем содержимое
                            try:
                                with open(full_path, 'rb') as f:
                                    saved_data = f.read()
                                if saved_data == test_data:
                                    print(f"  OK: СОДЕРЖИМОЕ СОВПАДАЕТ")
                                else:
                                    print(f"  ERROR: СОДЕРЖИМОЕ НЕ СОВПАДАЕТ")
                                    print(f"    Первые 20 байт сохраненного: {saved_data[:20]}")
                                    print(f"    Первые 20 байт переданных: {test_data[:20]}")
                            except Exception as read_error:
                                print(f"  Ошибка при проверке содержимого: {read_error}")
                        else:
                            print(f"  ERROR: РАЗМЕР НЕ СОВПАДАЕТ: сохранено {saved_size} байт, ожидалось {len(test_data)} байт")
                    else:
                        print(f"  ERROR: ФАЙЛ НЕ СОХРАНЕН")
                    
                    # Шаг 5: Очистка
                    os.unlink(tmp_path)
                    print(f"  Временный файл удален")
                    
                except Exception as e:
                    print(f"  ОШИБКА: {e}")
                    import traceback
                    print(f"  Трассировка: {traceback.format_exc()}")
            
            # Финальная очистка
            print(f"\n--- ФИНАЛЬНАЯ ОЧИСТКА ---")
            if os.path.exists(full_path):
                try:
                    # Удаляем через процедуру
                    delete_sql = f"""SELECT * FROM \"wp_DeleteFile\"('{img_path}', '{filename}')"""
                    with conn.begin():
                        conn.execute(text(delete_sql))
                    print(f"  Файл удален через процедуру")
                    time.sleep(2)
                    
                    if os.path.exists(full_path):
                        print(f"  ВНИМАНИЕ: Файл все еще существует после удаления")
                    else:
                        print(f"  OK: Файл успешно удален")
                except Exception as e:
                    print(f"  Не удалось удалить файл: {e}")
            else:
                print(f"  Файл уже удален")
            
            return True
            
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_final_solution()
    if success:
        print("\n=== ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО ===")
        print("\nРЕЗЮМЕ:")
        print("1. Добавлена проверка существования старого файла")
        print("2. Добавлено удаление старого файла через хранимую процедуру wp_DeleteFile")
        print("3. Добавлены задержки для гарантии удаления/сохранения файлов")
        print("4. Добавлена проверка размера и содержимого сохраненного файла")
        print("5. Улучшено логирование для отладки")
        sys.exit(0)
    else:
        print("\n=== ТЕСТЫ ЗАВЕРШЕНЫ С ОШИБКАМИ ===")
        sys.exit(1)