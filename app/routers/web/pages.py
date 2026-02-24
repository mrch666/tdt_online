from fastapi import APIRouter, Request, Depends, status, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import cast, String, text, bindparam, and_, or_, not_
from app.database import get_db
from app.models import Users, Storage, Modelgoods, Folders, ModelgoodsExternalImages
from app.config import settings
from app.routers.image_processing_utils import (
    is_jpg_file,
    optimize_external_image_processing,
    download_image_with_optimization
)
import logging
import requests
import tempfile
import os
from PIL import Image
import io

router = APIRouter(prefix="/web")
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)

@router.get("/modelgoods/{modelgoods_id}/details")
async def modelgoods_details(
    request: Request, 
    modelgoods_id: str,
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching modelgoods details for ID: {modelgoods_id}")
    
    try:
        logger.info(f"Searching for modelgoods with ID: '{modelgoods_id}'")
        modelgoods = db.query(Modelgoods).filter(Modelgoods.id.ilike(modelgoods_id)).first()
        
        if modelgoods:
            logger.info(f"Found modelgoods: ID={modelgoods.id}, Name={modelgoods.name}")
        else:
            logger.warning(f"No modelgoods found for ID: '{modelgoods_id}'")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    if not modelgoods:
        logger.warning(f"Modelgoods not found for ID: {modelgoods_id}")
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Проверяем, является ли запрос HTMX-запросом
    is_htmx = request.headers.get("HX-Request") == "true"
    logger.info(f"HTMX request: {is_htmx}")
    
    if is_htmx:
        # Для HTMX-запросов возвращаем только фрагмент
        return templates.TemplateResponse(
            "endpoints/modelgoods_details_fragment.html",
            {
                "request": request,
                "modelgoods": modelgoods,
                "description": modelgoods.comment if modelgoods and modelgoods.comment else ""
            }
        )
    else:
        # Для обычных запросов возвращаем полную страницу
        return templates.TemplateResponse(
            "endpoints/modelgoods_details.html",
            {
                "request": request,
                "current_page": 1,
                "total_pages": 1,
                "modelgoods": modelgoods,
                "description": modelgoods.comment if modelgoods and modelgoods.comment else ""
            }
        )

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "current_page": 1,
        "total_pages": 1
    })

@router.post("/login")
async def perform_login(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    try:
        username = form_data["username"].strip()
        password = form_data["password"].strip()
        logger.info(f"Attempting login with credentials: {username}/{password}")
        
        user = db.query(Users).filter(
            cast(Users.username, String).ilike(username),
            cast(Users.password, String).ilike(password)
        ).first()
        
        logger.info(f"Found user: {user.username if user else None}")
        
        if not user:
            return templates.TemplateResponse("login.html", 
                {"request": request, "error": "Неверные учетные данные", "current_page": 1, "total_pages": 1},
                status_code=status.HTTP_401_UNAUTHORIZED)
            
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="user", value=user.username)
        return response
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {str(e)}")
        return templates.TemplateResponse("login.html", 
            {"request": request, "error": "Ошибка сервера", "current_page": 1, "total_pages": 1},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Вспомогательные функции для работы с внешними изображениями

def download_and_convert_image(url: str) -> tempfile.NamedTemporaryFile:
    """
    Скачивает изображение с URL и конвертирует его в JPG.
    
    Args:
        url: URL изображения
        
    Returns:
        Временный файл с изображением в формате JPG
        
    Raises:
        HTTPException: Если не удалось скачать или конвертировать изображение
    """
    try:
        logger.info(f"Скачивание изображения с URL: {url}")
        
        # Скачиваем изображение
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Проверяем размер изображения
        content_length = len(response.content)
        logger.info(f"Размер скачанного изображения: {content_length} байт")
        
        if content_length == 0:
            raise HTTPException(status_code=400, detail="Пустое изображение")
        
        # Открываем изображение с помощью PIL
        img = Image.open(io.BytesIO(response.content))
        
        # Конвертируем в RGB если нужно (для PNG с прозрачностью)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Создаем белый фон
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Сохраняем во временный файл в формате JPG
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(temp_file, 'JPEG', quality=90, optimize=True)
        temp_file.flush()
        
        logger.info(f"Изображение сохранено во временный файл: {temp_file.name}")
        return temp_file
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при скачивании изображения: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Ошибка при скачивании изображения: {str(e)}")
    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Ошибка при обработке изображения: {str(e)}")


async def upload_to_main_api(modelid: str, image_file_path: str, db: Session = None) -> dict:
    """
    Загружает изображение через прямой вызов функции или API
    
    Args:
        modelid: ID модели товара
        image_file_path: Путь к файлу изображения
        db: Сессия базы данных (опционально)
        
    Returns:
        Результат загрузки в формате словаря
    """
    try:
        logger.info(f"Загрузка изображения для modelid={modelid}")
        
        # Проверяем размер файла перед отправкой
        file_size = os.path.getsize(image_file_path)
        logger.info(f"Размер файла для загрузки: {file_size} байт")
        
        if file_size == 0:
            logger.error("Пустой файл для загрузки")
            return {"status": "error", "message": "Пустой файл для загрузки"}
        
        # Читаем файл в память
        with open(image_file_path, 'rb') as f:
            file_content = f.read()
        
        # Получаем имя файла из пути
        filename = os.path.basename(image_file_path)
        
        # Если передан db, используем прямой вызов функции
        if db is not None:
            logger.info(f"Используем прямой вызов функции для загрузки изображения")
            try:
                from app.routers.image_processing_utils import process_image_directly
                
                result = await process_image_directly(
                    modelid=modelid,
                    image_content=file_content,
                    filename=filename,
                    db=db
                )
                
                if hasattr(result, 'dict'):
                    result_dict = result.dict()
                else:
                    result_dict = result
                
                if result_dict.get('status') == 'success':
                    logger.info(f"Успешная загрузка через прямой вызов: {result_dict}")
                    return {"status": "success", "message": "Изображение успешно загружено", "result": result_dict}
                else:
                    logger.error(f"Ошибка при прямой загрузке: {result_dict}")
                    return {"status": "error", "message": f"Ошибка загрузки: {result_dict.get('message', 'Неизвестная ошибка')}"}
                    
            except Exception as e:
                logger.error(f"Ошибка при прямом вызове функции: {str(e)}")
                # Пробуем использовать API как fallback
        
        # Используем API как fallback
        logger.info(f"Используем API как fallback для загрузки изображения")
        
        # Получаем URL API из конфигурации
        api_url = settings.get_modelgoods_image_url()
        logger.info(f"Используем API URL: {api_url}")
        
        # Создаем файловый объект из данных в памяти
        files = {'file': (f'{modelid}.jpg', file_content, 'image/jpeg')}
        data = {'modelid': modelid}
        
        # Логируем детали запроса
        logger.info(f"Отправка запроса к API: {api_url}")
        logger.info(f"Данные: modelid={modelid}, размер файла={file_size} байт")
        
        # Отправляем запрос к API с увеличенным таймаутом
        response = requests.post(
            api_url,
            files=files,
            data=data,
            timeout=120  # Увеличиваем таймаут для больших файлов
        )
            
        logger.info(f"Ответ API: статус {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Успешная загрузка: {result}")
            return result
        elif response.status_code == 404:
            logger.error(f"API endpoint не найден: {api_url}")
            return {"status": "error", "message": f"API endpoint не найден: {api_url}"}
        else:
            logger.error(f"Ошибка API: {response.status_code} - {response.text}")
            return {"status": "error", "message": f"Ошибка API: {response.status_code}: {response.text[:200]}"}
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Ошибка подключения к API {api_url}: {str(e)}")
        return {"status": "error", "message": f"Не удалось подключиться к API: {str(e)}"}
    except requests.exceptions.Timeout as e:
        logger.error(f"Таймаут при подключении к API {api_url}: {str(e)}")
        return {"status": "error", "message": f"Таймаут при подключении к API: {str(e)}"}
    except Exception as e:
        logger.error(f"Ошибка при загрузке: {str(e)}")
        return {"status": "error", "message": f"Ошибка при загрузке: {str(e)}"}


def get_products_with_external_images(db: Session, show_hidden: bool = False):
    """
    Получает товары с внешними изображениями, сгруппированные по modelid.
    
    Args:
        db: Сессия базы данных
        show_hidden: Показывать ли скрытые товары
        
    Returns:
        Список словарей с информацией о товарах и их изображениях
    """
    try:
        # Находим товары, у которых есть внешние изображения
        query = db.query(Modelgoods).join(
            ModelgoodsExternalImages,
            Modelgoods.id == ModelgoodsExternalImages.modelid
        )
        
        if not show_hidden:
            # Находим товары, у которых есть успешно загруженные изображения
            # (is_approved=1 и is_loaded_to_db=1)
            hidden_modelids = db.query(ModelgoodsExternalImages.modelid).filter(
                ModelgoodsExternalImages.is_approved == 1,
                ModelgoodsExternalImages.is_loaded_to_db == 1
            ).distinct().subquery()
            
            # Исключаем эти товары из запроса
            query = query.filter(~Modelgoods.id.in_(db.query(hidden_modelids.c.modelid)))
        
        # Получаем уникальные товары
        products = query.distinct().all()
        
        result = []
        for product in products:
            # Получаем все изображения для этого товара
            images = db.query(ModelgoodsExternalImages).filter(
                ModelgoodsExternalImages.modelid == product.id
            ).order_by(ModelgoodsExternalImages.created_at.desc()).all()
            
            # Проверяем, есть ли у товара подтвержденные но не загруженные изображения
            has_failed_uploads = any(
                img.is_approved == 1 and img.is_loaded_to_db == 0 
                for img in images
            )
            
            # Проверяем, скрыт ли товар (есть успешно загруженные изображения)
            is_hidden = any(
                img.is_approved == 1 and img.is_loaded_to_db == 1
                for img in images
            )
            
            result.append({
                'product': product,
                'images': images,
                'has_failed_uploads': has_failed_uploads,
                'is_hidden': is_hidden
            })
        
        logger.info(f"Найдено товаров с внешними изображениями: {len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при получении товаров с внешними изображениями: {str(e)}")
        raise


# Endpoint'ы для веб-страницы внешних изображений

@router.get("/external-images/")
async def external_images_page(
    request: Request, 
    db: Session = Depends(get_db),
    show_hidden: bool = False
):
    """
    Веб-страница для управления внешними изображениями товаров.
    
    Args:
        request: Запрос
        db: Сессия базы данных
        show_hidden: Показывать скрытые товары
        
    Returns:
        HTML страница с товарами и их внешними изображениями
    """
    try:
        logger.info(f"Загрузка страницы внешних изображений, show_hidden={show_hidden}")
        
        # Получаем товары с изображениями
        products_data = get_products_with_external_images(db, show_hidden)
        
        return templates.TemplateResponse(
            "endpoints/external_images.html",
            {
                "request": request,
                "products": products_data,
                "show_hidden": show_hidden
            }
        )
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке страницы внешних изображений: {str(e)}")
        return templates.TemplateResponse(
            "endpoints/external_images.html",
            {
                "request": request,
                "products": [],
                "show_hidden": show_hidden,
                "error": f"Ошибка при загрузке данных: {str(e)}"
            }
        )


@router.post("/external-images/{image_id}/process")
async def process_external_image(
    request: Request, 
    image_id: str, 
    db: Session = Depends(get_db)
):
    """
    Обрабатывает внешнее изображение: скачивает, конвертирует и загружает в основную БД.
    
    Args:
        request: Запрос
        image_id: ID изображения в таблице modelgoods_external_images
        db: Сессия базы данных
        
    Returns:
        JSON с результатом обработки
    """
    logger.info(f"Обработка внешнего изображения ID: {image_id}")
    
    try:
        # Получаем изображение из БД
        image = db.query(ModelgoodsExternalImages).filter_by(id=image_id).first()
        
        if not image:
            logger.error(f"Изображение с ID {image_id} не найдено")
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "Изображение не найдено"}
            )
        
        # Проверяем, не обработано ли уже изображение
        if image.is_approved == 1:
            logger.warning(f"Изображение {image_id} уже подтверждено")
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Изображение уже подтверждено"}
            )
        
        # Проверяем, является ли файл JPG для оптимизированной обработки
        filename_from_url = image.url.split('/')[-1].split('?')[0]
        
        if is_jpg_file(filename_from_url):
            logger.info(f"Файл {filename_from_url} является JPG, используем оптимизированную обработку")
            
            try:
                # Используем оптимизированную обработку
                result = await optimize_external_image_processing(
                    modelid=image.modelid,
                    image_url=image.url,
                    db=db
                )
                
                logger.info(f"Результат оптимизированной обработки: {result}")
                
                if result.get('status') == 'success':
                    # Успешная загрузка
                    image.is_approved = 1
                    image.is_loaded_to_db = 1
                    db.commit()
                    
                    logger.info(f"Изображение {image_id} успешно загружено в БД (оптимизированный путь)")
                    
                    # Проверяем, нужно ли скрывать весь товар
                    other_images = db.query(ModelgoodsExternalImages).filter(
                        ModelgoodsExternalImages.modelid == image.modelid,
                        ModelgoodsExternalImages.id != image.id
                    ).all()
                    
                    hide_product = not any(
                        img.is_approved == 1 and img.is_loaded_to_db == 1
                        for img in other_images
                    )
                    
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "message": "Изображение успешно загружено в БД (оптимизированный путь)",
                            "hide_product": hide_product
                        }
                    )
                else:
                    # Ошибка в оптимизированной обработке
                    image.is_approved = 1  # Отмечаем как подтвержденное
                    image.is_loaded_to_db = 0  # Но не загруженное в БД
                    db.commit()
                    
                    logger.error(f"Ошибка оптимизированной обработки изображения {image_id}: {result.get('message')}")
                    
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": False,
                            "message": f"Ошибка загрузки в БД: {result.get('message', 'Неизвестная ошибка')}",
                            "image_gray": True  # Флаг для серой миниатюры
                        }
                    )
                    
            except Exception as e:
                logger.error(f"Ошибка при оптимизированной обработке изображения {image_id}: {str(e)}")
                import traceback
                logger.error(f"Трассировка ошибки: {traceback.format_exc()}")
                # Пробуем стандартный путь как fallback
                logger.info(f"Пробуем стандартный путь обработки для изображения {image_id}")
        
        # Стандартная обработка (для не-JPG файлов или как fallback)
        temp_file = None
        try:
            temp_file = download_and_convert_image(image.url)
            
            # Загружаем через API
            api_result = await upload_to_main_api(image.modelid, temp_file.name, db)
            
            if api_result.get('status') == 'success':
                # Успешная загрузка
                image.is_approved = 1
                image.is_loaded_to_db = 1
                db.commit()
                
                logger.info(f"Изображение {image_id} успешно загружено в БД (стандартный путь)")
                
                # Проверяем, нужно ли скрывать весь товар
                other_images = db.query(ModelgoodsExternalImages).filter(
                    ModelgoodsExternalImages.modelid == image.modelid,
                    ModelgoodsExternalImages.id != image.id
                ).all()
                
                hide_product = not any(
                    img.is_approved == 1 and img.is_loaded_to_db == 1
                    for img in other_images
                )
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Изображение успешно загружено в БД",
                        "hide_product": hide_product
                    }
                )
            else:
                # Ошибка загрузки через API
                image.is_approved = 1  # Отмечаем как подтвержденное
                image.is_loaded_to_db = 0  # Но не загруженное в БД
                db.commit()
                
                logger.error(f"Ошибка загрузки изображения {image_id} через API: {api_result.get('message')}")
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": False,
                        "message": f"Ошибка загрузки в БД: {api_result.get('message', 'Неизвестная ошибка')}",
                        "image_gray": True  # Флаг для серой миниатюры
                    }
                )
                
        except HTTPException as e:
            # Ошибка при скачивании или конвертации
            logger.error(f"Ошибка обработки изображения {image_id}: {e.detail}")
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": f"Ошибка обработки изображения: {e.detail}"
                }
            )
            
        finally:
            # Удаляем временный файл с повторными попытками
            if temp_file and os.path.exists(temp_file.name):
                max_attempts = 3
                for attempt in range(max_attempts):
                    try:
                        os.unlink(temp_file.name)
                        logger.info(f"Временный файл удален: {temp_file.name}")
                        break
                    except (PermissionError, OSError) as e:
                        if attempt == max_attempts - 1:
                            # Последняя попытка - логируем предупреждение
                            logger.warning(f"Не удалось удалить временный файл после {max_attempts} попыток: {str(e)}")
                        else:
                            # Ждем перед следующей попыткой (100ms)
                            import time
                            time.sleep(0.1)
                    except Exception as e:
                        # Другие ошибки логируем как предупреждение
                        logger.warning(f"Ошибка при удалении временного файла: {str(e)}")
                        break
                    
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке изображения {image_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Внутренняя ошибка сервера: {str(e)}"
            }
        )
