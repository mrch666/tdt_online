"""
Тест для проверки медленной загрузки изображений
"""
import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from sqlalchemy.orm import Session
import asyncio

def test_image_upload_has_excessive_sleeps():
    """
    Тест проверяет, что в коде загрузки изображений нет излишних задержек
    """
    from app.routers.modelgoods_images import upload_model_image
    
    # Мокаем все зависимости
    with patch('app.routers.modelgoods_images.os.path.exists') as mock_exists:
        with patch('app.routers.modelgoods_images.os.unlink') as mock_unlink:
            with patch('app.routers.modelgoods_images.os.path.getsize') as mock_getsize:
                with patch('app.routers.modelgoods_images.tempfile.NamedTemporaryFile') as mock_tempfile:
                    # Настраиваем моки
                    mock_exists.return_value = False
                    
                    # Мокаем временный файл
                    mock_temp = MagicMock()
                    mock_temp.name = "C:\\temp\\test.jpg"
                    mock_temp.__enter__.return_value = mock_temp
                    mock_tempfile.return_value = mock_temp
                    
                    # Создаем мок сессии БД
                    mock_db = MagicMock(spec=Session)
                    
                    # Мокаем запросы к БД
                    mock_result = MagicMock()
                    mock_result.fetchone.return_value = ["0000010028Vx"]
                    mock_db.execute.return_value = mock_result
                    
                    # Мокаем процедуру сохранения
                    mock_procedure_result = [(1,)]
                    mock_db.execute.return_value.fetchall.return_value = mock_procedure_result
                    
                    # Мокаем UploadFile
                    mock_file = AsyncMock()
                    mock_file.filename = "test.jpg"
                    mock_file.read.return_value = b"test image content"
                    mock_file.close = AsyncMock()
                    
                    # Мокаем open для чтения временного файла
                    mock_file_obj = MagicMock()
                    mock_file_obj.read.return_value = b"test image content"
                    
                    # Мокаем time.sleep, чтобы проверить, сколько раз он вызывается
                    with patch('time.sleep') as mock_sleep:
                        # Вызываем функцию
                        try:
                            result = asyncio.run(upload_model_image(
                                modelid="0000010028Vx",
                                file=mock_file,
                                db=mock_db
                            ))
                            
                            # Проверяем, что time.sleep вызывался не более 2 раз
                            # В коде есть:
                            # 1. time.sleep(1) после удаления файла через процедуру
                            # 2. time.sleep(2) после проверки существования файла
                            # 3. time.sleep(1) после успешного сохранения
                            # Это слишком много!
                            call_count = mock_sleep.call_count
                            assert call_count <= 2, f"Слишком много задержек: {call_count} вызовов time.sleep"
                            
                        except Exception as e:
                            # Если функция выбросила исключение, это нормально для теста
                            # Главное - проверить количество вызовов time.sleep
                            call_count = mock_sleep.call_count
                            assert call_count <= 2, f"Слишком много задержек: {call_count} вызовов time.sleep"

def test_remove_excessive_sleeps():
    """
    Тест проверяет, что после исправления кода задержки уменьшены
    """
    # Прочитаем код и посчитаем количество time.sleep
    import re
    
    with open('app/routers/modelgoods_images.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем все вызовы time.sleep
    sleep_calls = re.findall(r'time\.sleep\(', content)
    
    # В идеале должно быть не более 1 вызова time.sleep
    assert len(sleep_calls) <= 1, f"Слишком много вызовов time.sleep в коде: {len(sleep_calls)}"

def test_external_images_hide_logic_works():
    """
    Тест проверяет, что логика скрытия товаров работает правильно
    """
    import re
    
    # Прочитаем код страницы внешних изображений
    with open('app/routers/web/pages.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем логику скрытия товаров
    hide_pattern = r'hide_product.*=.*not any'
    hide_matches = re.findall(hide_pattern, content, re.DOTALL)
    
    # Должна быть логика скрытия
    assert len(hide_matches) > 0, "Не найдена логика скрытия товаров"
    
    # Проверяем, что логика правильная
    # Товар должен скрываться, если у него нет успешно загруженных изображений
    # Ищем точную строку из кода
    correct_logic = "hide_product = not any("
    assert correct_logic in content, f"Неправильная логика скрытия товаров"
    
    # Проверяем, что есть проверка is_approved и is_loaded_to_db
    assert "img.is_approved == 1" in content, "Нет проверки is_approved"
    assert "img.is_loaded_to_db == 1" in content, "Нет проверки is_loaded_to_db"

def test_file_save_optimization():
    """
    Тест проверяет оптимизацию сохранения файлов
    """
    # Проверяем, что нет излишних проверок существования файлов
    with open('app/routers/modelgoods_images.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Считаем количество проверок os.path.exists
    exists_calls = content.count('os.path.exists')
    
    # Должно быть не более 3 проверок (для старого файла, проверки после удаления и проверки сохранения)
    assert exists_calls <= 3, f"Слишком много проверок существования файлов: {exists_calls}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])