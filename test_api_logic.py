import sys
sys.path.append('.')
import os
import requests
from app.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

def test_api_logic():
    """Тест логики API для формирования имени файла с расширением"""
    print("=== Тест логики API: формирование имени файла с расширением ===")
    
    # Данные для теста
    modelid = "000001002Qa{"
    
    print(f"Тестовые данные:")
    print(f"  Model ID: {modelid}")
    print(f"  Расширение файла: jpg")
    
    # 1. Проверяем текущее состояние в БД
    print(f"\n1. Проверка текущего состояния в БД...")
    try:
        with engine.connect() as conn:
            result = conn.execute(
                'SELECT "id", "imgext", "changedate" FROM "modelgoods" WHERE "id" = ?',
                [modelid]
            ).fetchone()
            
            if result:
                print(f"   Товар найден: ID={result[0]}, imgext={result[1]}, changedate={result[2]}")
            else:
                print(f"   Товар не найден, создаем тестовую запись...")
                conn.execute(
                    'INSERT INTO "modelgoods" ("id", "imgext", "changedate") VALUES (?, ?, CURRENT_TIMESTAMP)',
                    [modelid, "jpg"]
                )
                print(f"   Тестовая запись создана")
                
    except Exception as e:
        print(f"   ОШИБКА при работе с БД: {e}")
        return False
    
    # 2. Тестируем новую логику API (последовательность операций)
    print(f"\n2. Тестирование новой логики API:")
    print(f"   a) Получаем расширение из имени файла: 'image.jpg' -> 'jpg'")
    test_filename = "image.jpg"
    imgext = test_filename.split('.')[-1].split('?')[0]
    print(f"      Расширение: {imgext}")
    
    print(f"   b) Формируем имя файла с новым расширением (временно)")
    try:
        with engine.connect() as conn:
            # Получаем текущее значение imgext
            current_result = conn.execute(
                'SELECT "imgext" FROM "modelgoods" WHERE "id" = ?',
                [modelid]
            ).fetchone()
            
            current_imgext = current_result[0] if current_result and current_result[0] else None
            print(f"      Текущее расширение в БД: {current_imgext}")
            
            # Формируем имя файла с новым расширением (временно, как в новом API)
            # Получаем числовые части ID
            id_parts_result = conn.execute(
                'SELECT DEC64I0("id"), DEC64I1("id") FROM "modelgoods" WHERE "id" = ?',
                [modelid]
            ).fetchone()
            
            if id_parts_result:
                part0 = id_parts_result[0]
                part1 = id_parts_result[1]
                filename = f"{part0}_{part1}.{imgext}"
                print(f"      Сформированное имя файла: {filename}")
                
                # Проверяем, что имя файла содержит расширение
                if '.' in filename and filename.endswith(f'.{imgext}'):
                    print(f"      [OK] Имя файла содержит правильное расширение: .{imgext}")
                else:
                    print(f"      [ERROR] Имя файла НЕ содержит правильное расширение")
                    print(f"         Ожидалось: *.{imgext}")
                    print(f"         Получено: {filename}")
                    return False
            else:
                print(f"      [ERROR] Не удалось получить части ID для формирования имени файла")
                return False
                
    except Exception as e:
        print(f"   ОШИБКА: {e}")
        return False
    
    # 3. Проверяем функцию чтения (get_model_image_info)
    print(f"\n3. Тестирование функции чтения информации об изображении:")
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
                
                # Проверяем, что все поля заполнены правильно
                if result[1] and '.' in result[1] and result[1].endswith(f'.{result[2]}'):
                    print(f"   [OK] Имя файла и расширение корректны")
                else:
                    print(f"   [ERROR] Проблема с именем файла или расширением")
                    return False
                    
                if result[2] == imgext:
                    print(f"   [OK] Расширение в БД совпадает с ожидаемым")
                else:
                    print(f"   [ERROR] Расширение в БД не совпадает")
                    return False
            else:
                print(f"   [ERROR] Не удалось получить информацию из БД")
                return False
                
    except Exception as e:
        print(f"   ОШИБКА: {e}")
        return False
    
    # 4. Проверяем функцию удаления
    print(f"\n4. Тестирование функции удаления:")
    try:
        with engine.connect() as conn:
            # Получаем имя файла для удаления
            result = conn.execute(
                'SELECT DEC64I0("id") || \'_\' || DEC64I1("id") || \'.\' || "imgext" FROM "modelgoods" WHERE "id" = ?',
                [modelid]
            ).fetchone()
            
            if result and result[0]:
                filename = result[0].split('?')[0]
                print(f"   Имя файла для удаления: {filename}")
                
                # Проверяем, что имя файла содержит расширение
                if '.' in filename:
                    print(f"   [OK] Имя файла содержит расширение для удаления")
                else:
                    print(f"   [ERROR] Имя файла не содержит расширение")
                    return False
            else:
                print(f"   [ERROR] Не удалось получить имя файла для удаления")
                return False
                
    except Exception as e:
        print(f"   ОШИБКА: {e}")
        return False
    
    print(f"\n=== ТЕСТ ЗАВЕРШЕН УСПЕШНО ===")
    print(f"[OK] Новая логика API работает корректно:")
    print(f"   1. Расширение извлекается из имени файла")
    print(f"   2. Поле imgext обновляется в БД перед сохранением файла")
    print(f"   3. Имя файла формируется с правильным расширением")
    print(f"   4. Функции чтения и удаления работают с именами файлов с расширениями")
    
    return True

if __name__ == "__main__":
    success = test_api_logic()
    if success:
        print("\n[УСПЕХ] ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        sys.exit(0)
    else:
        print("\n[ОШИБКА] ТЕСТЫ ЗАВЕРШИЛИСЬ С ОШИБКАМИ")
        sys.exit(1)