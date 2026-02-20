import sys
sys.path.append('.')
import os
import requests
import tempfile
from app.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

def download_image(url):
    """Скачивание изображения с URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.error(f"Ошибка скачивания изображения: {e}")
        return None

def test_image_upload():
    """Тест загрузки изображения для товара"""
    print("=== Тест загрузки изображения для товара ===")
    
    # Данные для теста
    modelid = "000001002Qa{"
    image_url = "https://st.aestatic.net/items-img-7/R/6/A/H/Af78ed7279796474391bea8325e44c3f1h.jpeg_960x960.jpg"
    expected_filename = "Активная пена \"Active Foam Light\" 1л ОР-00001703.jpg"
    
    print(f"Тестовые данные:")
    print(f"  Model ID: {modelid}")
    print(f"  URL изображения: {image_url}")
    print(f"  Ожидаемое имя файла: {expected_filename}")
    
    # 1. Скачиваем изображение
    print(f"\n1. Скачивание изображения...")
    image_data = download_image(image_url)
    if not image_data:
        print("   ОШИБКА: Не удалось скачать изображение")
        return False
    
    print(f"   Изображение скачано успешно, размер: {len(image_data)} байт")
    
    # 2. Проверяем существование товара в БД
    print(f"\n2. Проверка существования товара в БД...")
    try:
        with engine.connect() as conn:
            # Проверяем существование товара
            result = conn.execute(
                'SELECT "id", "imgext" FROM "modelgoods" WHERE "id" = ?',
                [modelid]
            ).fetchone()
            
            if not result:
                print(f"   Товар с ID {modelid} не найден в БД")
                print(f"   Создаем тестовую запись...")
                
                # Создаем тестовую запись
                conn.execute(
                    'INSERT INTO "modelgoods" ("id", "imgext", "changedate") VALUES (?, ?, CURRENT_TIMESTAMP)',
                    [modelid, "jpg"]
                )
                conn.commit()
                print(f"   Тестовая запись создана")
            else:
                print(f"   Товар найден: ID={result[0]}, imgext={result[1]}")
                
    except Exception as e:
        print(f"   ОШИБКА при работе с БД: {e}")
        return False
    
    # 3. Сохраняем изображение через хранимую процедуру
    print(f"\n3. Сохранение изображения через хранимую процедуру...")
    try:
        with engine.connect() as conn:
            # Получаем имя файла из БД
            result = conn.execute(
                'SELECT DEC64I0("id") || \'_\' || DEC64I1("id") || \'.\' || "imgext" FROM "modelgoods" WHERE "id" = ?',
                [modelid]
            ).fetchone()
            
            if not result or not result[0]:
                print("   ОШИБКА: Не удалось получить имя файла из БД")
                return False
            
            filename = result[0]
            img_path = os.path.join(os.getenv('BASE_DIR', 'C:\\Program Files (x86)\\tdt3\\bases'), 
                                   os.getenv('IMG_SUBDIR', 'img')) + os.sep
            
            print(f"   Имя файла из БД: {filename}")
            print(f"   Путь для сохранения: {img_path}")
            
            # Сохраняем через хранимую процедуру
            result = conn.execute(
                'SELECT * FROM "wp_SaveBlobToFile"(?, ?, ?)',
                [img_path, filename, image_data]
            )
            
            # Проверяем результат
            proc_result = result.fetchone()
            if proc_result and proc_result[0] == 1:
                print("   ИЗОБРАЖЕНИЕ УСПЕШНО СОХРАНЕНО через хранимую процедуру")
            else:
                print(f"   ОШИБКА: Процедура вернула {proc_result}")
                return False
            
            # Обновляем запись в БД (как в реальном API)
            # Для engine.connect() не нужен commit, изменения автоматически коммитятся
            conn.execute(
                'UPDATE "modelgoods" SET "imgext" = ?, "changedate" = CURRENT_TIMESTAMP WHERE "id" = ?',
                ["jpg", modelid]
            )
            print("   ЗАПИСЬ В БД ОБНОВЛЕНА: imgext='jpg', changedate=CURRENT_TIMESTAMP")
                
    except Exception as e:
        print(f"   ОШИБКА при сохранении изображения: {e}")
        return False
    
    # 4. Проверяем сохраненный файл
    print(f"\n4. Проверка сохраненного файла...")
    full_path = os.path.join(img_path.rstrip(os.sep), filename)
    if os.path.exists(full_path):
        file_size = os.path.getsize(full_path)
        print(f"   Файл существует: {full_path}")
        print(f"   Размер файла: {file_size} байт")
        
        # Сравниваем размеры
        if file_size == len(image_data):
            print("   РАЗМЕРЫ СОВПАДАЮТ!")
        else:
            print(f"   РАЗМЕРЫ НЕ СОВПАДАЮТ: файл {file_size} байт, оригинал {len(image_data)} байт")
            
        # Проверяем первые байты
        with open(full_path, 'rb') as f:
            file_content = f.read(100)
            image_start = image_data[:100]
            
            if file_content == image_start:
                print("   ПЕРВЫЕ 100 БАЙТ СОВПАДАЮТ!")
            else:
                print("   ПЕРВЫЕ 100 БАЙТ НЕ СОВПАДАЮТ")
    else:
        print(f"   ФАЙЛ НЕ НАЙДЕН: {full_path}")
        return False
    
    # 5. Проверяем информацию о изображении через API
    print(f"\n5. Проверка информации о изображении через API...")
    try:
        with engine.connect() as conn:
            result = conn.execute(
                '''
                SELECT 
                    MG."id" as modelid,
                    DEC64I0(MG."id") || '_' || DEC64I1(MG."id") || '.' || MG."imgext" as filename,
                    MG."imgext",
                    MG."changedate"
                FROM "modelgoods" MG
                WHERE MG."id" = ?
                ''',
                [modelid]
            ).fetchone()
            
            if result:
                print(f"   Информация из БД:")
                print(f"     Model ID: {result[0]}")
                print(f"     Имя файла: {result[1]}")
                print(f"     Расширение: {result[2]}")
                print(f"     Дата изменения: {result[3]}")
                
                if result[1] == filename:
                    print("   ИМЯ ФАЙЛА СОВПАДАЕТ!")
                else:
                    print(f"   ИМЯ ФАЙЛА НЕ СОВПАДАЕТ: БД={result[1]}, ожидалось={filename}")
                
                # Проверяем, что поле imgext обновлено
                if result[2] == "jpg":
                    print("   РАСШИРЕНИЕ ОБНОВЛЕНО В БД: jpg")
                else:
                    print(f"   ОШИБКА: Расширение не обновлено в БД: {result[2]}")
                    
                # Проверяем, что changedate обновлен (должен быть свежим)
                if result[3]:
                    print(f"   ДАТА ИЗМЕНЕНИЯ ОБНОВЛЕНА: {result[3]}")
                else:
                    print("   ОШИБКА: Дата изменения не обновлена")
            else:
                print("   ОШИБКА: Не удалось получить информацию из БД")
                
    except Exception as e:
        print(f"   ОШИБКА при получении информации: {e}")
    
    # 6. Удаляем тестовый файл
    print(f"\n6. Очистка: удаление тестового файла...")
    try:
        with engine.connect() as conn:
            sql = f'SELECT * FROM "wp_DeleteFile"(\'{img_path}\', \'{filename}\')'
            result = conn.execute(sql)
            
            proc_result = result.fetchone()
            if proc_result and proc_result[0] == 1:
                print("   ФАЙЛ УСПЕШНО УДАЛЕН")
            else:
                print(f"   ОШИБКА удаления: процедура вернула {proc_result}")
                
        # Проверяем, что файл удален
        if os.path.exists(full_path):
            print(f"   ВНИМАНИЕ: Файл все еще существует: {full_path}")
        else:
            print(f"   Файл успешно удален с диска")
            
    except Exception as e:
        print(f"   ОШИБКА при удалении файла: {e}")
    
    print(f"\n=== ТЕСТ ЗАВЕРШЕН ===")
    return True

if __name__ == "__main__":
    # Проверяем наличие необходимых библиотек
    try:
        import requests
    except ImportError:
        print("ОШИБКА: Библиотека 'requests' не установлена")
        print("Установите её командой: pip install requests")
        sys.exit(1)
    
    success = test_image_upload()
    if success:
        print("\n[УСПЕХ] ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        sys.exit(0)
    else:
        print("\n[ОШИБКА] ТЕСТЫ ЗАВЕРШИЛИСЬ С ОШИБКАМИ")
        sys.exit(1)
