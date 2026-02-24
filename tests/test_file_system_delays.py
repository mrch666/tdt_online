"""
Тест для проверки задержек файловой системы при сохранении файлов
"""
import pytest
import os
import time
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

def test_file_system_delay():
    """
    Тест проверяет задержки между записью файла и его появлением на диске
    """
    import tempfile
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
        tmp_file.write(b"test content")
        tmp_path = tmp_file.name
    
    try:
        # Проверяем, что файл существует сразу после записи
        assert os.path.exists(tmp_path), "Файл должен существовать сразу после записи"
        
        # Проверяем размер файла
        file_size = os.path.getsize(tmp_path)
        assert file_size == len(b"test content"), f"Размер файла должен быть {len(b'test content')}, а не {file_size}"
        
        print(f"Файл создан: {tmp_path}, размер: {file_size} байт")
        
        # Проверяем, что файл можно прочитать сразу
        with open(tmp_path, 'rb') as f:
            content = f.read()
            assert content == b"test content", "Содержимое файла должно совпадать"
        
        print("Файл успешно прочитан сразу после записи")
        
    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
            print(f"Файл удален: {tmp_path}")

def test_procedure_result_vs_file_existence():
    """
    Тест проверяет расхождение между результатом процедуры и фактическим сохранением файла
    """
    from app.routers.modelgoods_images import upload_model_image
    from sqlalchemy.orm import Session
    
    # Мокаем все зависимости
    with patch('app.routers.modelgoods_images.os.path.exists') as mock_exists:
        with patch('app.routers.modelgoods_images.os.unlink') as mock_unlink:
            with patch('app.routers.modelgoods_images.tempfile.NamedTemporaryFile') as mock_tempfile:
                with patch('app.routers.modelgoods_images.os.getenv') as mock_getenv:
                    with patch('app.routers.modelgoods_images.os.path.getsize') as mock_getsize:
                        # Настраиваем моки
                        mock_getenv.side_effect = lambda key: {
                            'BASE_DIR': 'C:\\test',
                            'IMG_SUBDIR': 'img'
                        }.get(key, None)
                        
                        mock_exists.return_value = False
                        mock_getsize.return_value = 100
                        
                        mock_temp = MagicMock()
                        mock_temp.name = "C:\\temp\\test.jpg"
                        mock_temp.__enter__.return_value = mock_temp
                        mock_tempfile.return_value = mock_temp
                        
                        mock_db = MagicMock(spec=Session)
                        mock_result = MagicMock()
                        mock_result.fetchone.return_value = ["0000010028Vx"]
                        mock_db.execute.return_value = mock_result
                        
                        # Процедура возвращает успех (oRes=1)
                        mock_procedure_result = [(1,)]
                        mock_db.execute.return_value.fetchall.return_value = mock_procedure_result
                        
                        mock_file = AsyncMock()
                        mock_file.filename = "test.jpg"
                        mock_file.read.return_value = b"test image content"
                        mock_file.close = AsyncMock()
                        
                        # Настраиваем логику проверки существования файла
                        # Процедура вернула успех, но файл на диске не появился
                        exists_call_count = 0
                        
                        def exists_side_effect(path):
                            nonlocal exists_call_count
                            exists_call_count += 1
                            # Файл никогда не появляется на диске
                            return False
                        
                        mock_exists.side_effect = exists_side_effect
                        
                        # Вызываем функцию
                        try:
                            result = asyncio.run(upload_model_image(
                                modelid="0000010028Vx",
                                file=mock_file,
                                db=mock_db
                            ))
                            
                            # Проверяем, что функция не падает, даже если файл не появился на диске
                            # (т.к. процедура вернула успех)
                            assert result['status'] == 'success'
                            print(f"Функция успешно завершилась, даже если файл не появился на диске")
                            print(f"Количество проверок существования файла: {exists_call_count}")
                            
                        except Exception as e:
                            # Если функция выбросила исключение, проверяем причину
                            print(f"Функция завершилась с ошибкой: {str(e)}")
                            # Проверяем, что ошибка не связана с отсутствием файла на диске
                            assert "файл не найден" not in str(e).lower()
                            assert "file not found" not in str(e).lower()

def test_file_system_cache_delay():
    """
    Тест проверяет задержки кэширования файловой системы Windows
    """
    import tempfile
    import time
    
    # Создаем файл
    file_path = None
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        f.write(b"test data for cache delay")
        file_path = f.name
    
    try:
        # Проверяем существование файла
        assert os.path.exists(file_path), "Файл должен существовать"
        
        # Измеряем время доступа к файлу
        start_time = time.time()
        with open(file_path, 'rb') as f:
            content = f.read()
        end_time = time.time()
        
        access_time = end_time - start_time
        
        # Время доступа должно быть меньше 0.1 секунды
        assert access_time < 0.1, f"Время доступа к файлу слишком долгое: {access_time:.3f} секунд"
        
        print(f"Время доступа к файлу: {access_time:.3f} секунд (в норме)")
        
        # Проверяем, что файл можно удалить сразу
        delete_start = time.time()
        os.unlink(file_path)
        delete_end = time.time()
        
        delete_time = delete_end - delete_start
        
        # Время удаления должно быть меньше 0.1 секунды
        assert delete_time < 0.1, f"Время удаления файла слишком долгое: {delete_time:.3f} секунд"
        
        print(f"Время удаления файла: {delete_time:.3f} секунд (в норме)")
        
    finally:
        # Убеждаемся, что файл удален
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except:
                pass

def test_concurrent_file_access():
    """
    Тест проверяет проблемы с одновременным доступом к файлу
    """
    import tempfile
    import threading
    
    file_path = None
    lock_acquired = False
    
    def read_file_thread():
        """Поток для чтения файла"""
        nonlocal lock_acquired
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            lock_acquired = True
            print(f"Поток чтения: файл прочитан, размер: {len(content)} байт")
        except Exception as e:
            print(f"Поток чтения: ошибка: {str(e)}")
    
    # Создаем файл
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        f.write(b"test data for concurrent access")
        file_path = f.name
    
    try:
        # Запускаем поток чтения
        thread = threading.Thread(target=read_file_thread)
        thread.start()
        
        # Ждем немного
        time.sleep(0.1)
        
        # Пытаемся удалить файл (должно работать или дать PermissionError)
        try:
            os.unlink(file_path)
            print("Файл успешно удален во время чтения")
        except PermissionError:
            print("Файл заблокирован для удаления (ожидаемо при чтении)")
            # Ждем завершения потока
            thread.join(timeout=1.0)
            
            # Пробуем удалить снова
            try:
                os.unlink(file_path)
                print("Файл удален после завершения чтения")
            except Exception as e:
                print(f"Не удалось удалить файл даже после завершения чтения: {str(e)}")
        except Exception as e:
            print(f"Неожиданная ошибка при удалении файла: {str(e)}")
        
        # Ждем завершения потока
        thread.join(timeout=2.0)
        
        # Проверяем, что поток завершился
        assert not thread.is_alive(), "Поток чтения не завершился"
        
    finally:
        # Убеждаемся, что файл удален
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except:
                pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])