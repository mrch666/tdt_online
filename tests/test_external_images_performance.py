"""
Тесты для проверки производительности загрузки изображений и скрытия товаров
"""
import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from sqlalchemy.orm import Session
import asyncio

def test_image_upload_performance():
    """
    Тест проверяет, что загрузка изображения не занимает слишком много времени
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
                    mock_temp.name = "/tmp/test.jpg"
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
                    
                    # Замеряем время выполнения
                    start_time = time.time()
                    
                    try:
                        # Вызываем функцию (синхронно, так как она асинхронная)
                        result = asyncio.run(upload_model_image(
                            modelid="0000010028Vx",
                            file=mock_file,
                            db=mock_db
                        ))
                        
                        end_time = time.time()
                        execution_time = end_time - start_time
                        
                        # Проверяем, что выполнение заняло не более 3 секунд
                        assert execution_time < 3.0, f"Загрузка изображения заняла {execution_time:.2f} секунд, что слишком долго"
                        
                        # Проверяем, что функция вернула успех
                        assert result.status == "success"
                        
                    except Exception as e:
                        pytest.fail(f"Функция выбросила исключение: {e}")

def test_external_images_hide_logic():
    """
    Тест проверяет логику скрытия товаров после успешной загрузки изображения
    """
    from app.routers.web.pages import process_external_image
    from fastapi import Request
    
    # Мокаем все зависимости
    with patch('app.routers.web.pages.ModelgoodsExternalImages') as mock_model:
        # Создаем мок изображения
        mock_image = MagicMock()
        mock_image.id = "test_id"
        mock_image.modelid = "0000010028Vx"
        mock_image.url = "https://example.com/test.jpg"
        mock_image.is_approved = 0
        mock_image.is_loaded_to_db = 0
        
        # Создаем мок сессии БД
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_image
        mock_db.query.return_value = mock_query
        
        # Мокаем другие изображения для этого товара
        mock_other_image = MagicMock()
        mock_other_image.is_approved = 0
        mock_other_image.is_loaded_to_db = 0
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_other_image]
        
        # Мокаем download_and_convert_image
        with patch('app.routers.web.pages.download_and_convert_image') as mock_download:
            # Создаем мок временного файла
            mock_tempfile = MagicMock()
            mock_tempfile.name = "C:\\test\\tempfile.jpg"
            mock_download.return_value = mock_tempfile
            
            # Мокаем upload_to_main_api
            with patch('app.routers.web.pages.upload_to_main_api') as mock_upload:
                mock_upload.return_value = {"status": "success"}
                
                # Мокаем os.path.exists и os.unlink
                with patch('app.routers.web.pages.os.path.exists') as mock_exists:
                    with patch('app.routers.web.pages.os.unlink') as mock_unlink:
                        mock_exists.return_value = True
                        
                        # Вызываем функцию асинхронно
                        result = asyncio.run(process_external_image(
                            request=MagicMock(spec=Request),
                            image_id="test_id",
                            db=mock_db
                        ))
                        
                        # Проверяем, что функция вернула успех
                        assert result.status_code == 200
                        
                        # Проверяем, что hide_product = True (это первое успешно загруженное изображение)
                        import json
                        result_data = json.loads(result.body.decode())
                        assert result_data["hide_product"] == True, "Товар должен скрываться после первой успешной загрузки"

def test_external_images_not_hide_when_other_images_exist():
    """
    Тест проверяет, что товар не скрывается, если у него уже есть успешно загруженные изображения
    """
    from app.routers.web.pages import process_external_image
    from fastapi import Request
    
    # Мокаем все зависимости
    with patch('app.routers.web.pages.ModelgoodsExternalImages') as mock_model:
        # Создаем мок изображения
        mock_image = MagicMock()
        mock_image.id = "test_id"
        mock_image.modelid = "0000010028Vx"
        mock_image.url = "https://example.com/test.jpg"
        mock_image.is_approved = 0
        mock_image.is_loaded_to_db = 0
        
        # Создаем мок сессии БД
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_image
        mock_db.query.return_value = mock_query
        
        # Мокаем другие изображения для этого товара (одно уже успешно загружено)
        mock_other_image = MagicMock()
        mock_other_image.is_approved = 1
        mock_other_image.is_loaded_to_db = 1
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_other_image]
        
        # Мокаем download_and_convert_image
        with patch('app.routers.web.pages.download_and_convert_image') as mock_download:
            # Создаем мок временного файла
            mock_tempfile = MagicMock()
            mock_tempfile.name = "C:\\test\\tempfile.jpg"
            mock_download.return_value = mock_tempfile
            
            # Мокаем upload_to_main_api
            with patch('app.routers.web.pages.upload_to_main_api') as mock_upload:
                mock_upload.return_value = {"status": "success"}
                
                # Мокаем os.path.exists и os.unlink
                with patch('app.routers.web.pages.os.path.exists') as mock_exists:
                    with patch('app.routers.web.pages.os.unlink') as mock_unlink:
                        mock_exists.return_value = True
                        
                        # Вызываем функцию асинхронно
                        result = asyncio.run(process_external_image(
                            request=MagicMock(spec=Request),
                            image_id="test_id",
                            db=mock_db
                        ))
                        
                        # Проверяем, что функция вернула успех
                        assert result.status_code == 200
                        
                        # Проверяем, что hide_product = False (уже есть успешно загруженные изображения)
                        import json
                        result_data = json.loads(result.body.decode())
                        assert result_data["hide_product"] == False, "Товар не должен скрываться, если уже есть успешно загруженные изображения"

def test_file_save_delay_handling():
    """
    Тест проверяет обработку задержек при сохранении файлов
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
                    mock_temp.name = "/tmp/test.jpg"
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
                    
                    # Мокаем time.sleep, чтобы проверить, что он вызывается
                    with patch('app.routers.modelgoods_images.time.sleep') as mock_sleep:
                        # Вызываем функцию
                        result = asyncio.run(upload_model_image(
                            modelid="0000010028Vx",
                            file=mock_file,
                            db=mock_db
                        ))
                        
                        # Проверяем, что time.sleep был вызван (для проверки файла на диске)
                        # В коде есть time.sleep(1) после успешного сохранения
                        mock_sleep.assert_called_with(1)

def test_get_products_with_external_images_hidden_logic():
    """
    Тест проверяет логику получения товаров с внешними изображениями
    """
    from app.routers.web.pages import get_products_with_external_images
    
    # Мокаем все зависимости
    with patch('app.routers.web.pages.Modelgoods') as mock_modelgoods:
        with patch('app.routers.web.pages.ModelgoodsExternalImages') as mock_external_images:
            # Создаем мок сессии БД
            mock_db = MagicMock(spec=Session)
            
            # Создаем мок товара
            mock_product = MagicMock()
            mock_product.id = "0000010028Vx"
            mock_product.name = "Test Product"
            
            # Создаем мок изображения
            mock_image = MagicMock()
            mock_image.modelid = "0000010028Vx"
            mock_image.is_approved = 1
            mock_image.is_loaded_to_db = 1
            
            # Настраиваем моки запросов
            mock_query = MagicMock()
            mock_query.join.return_value.distinct.return_value.all.return_value = [mock_product]
            mock_db.query.return_value = mock_query
            
            # Мокаем подзапрос для скрытых товаров
            mock_subquery = MagicMock()
            mock_subquery.c.modelid = "0000010028Vx"
            mock_db.query.return_value.filter.return_value.distinct.return_value.subquery.return_value = mock_subquery
            
            # Мокаем запрос изображений для товара
            mock_image_query = MagicMock()
            mock_image_query.filter.return_value.order_by.return_value.all.return_value = [mock_image]
            mock_db.query.return_value = mock_image_query
            
            # Вызываем функцию с show_hidden=False
            result = get_products_with_external_images(mock_db, show_hidden=False)
            
            # Проверяем результат
            assert len(result) == 1
            assert result[0]['product'].id == "0000010028Vx"
            assert result[0]['is_hidden'] == True  # Товар должен быть скрыт

if __name__ == "__main__":
    pytest.main([__file__, "-v"])