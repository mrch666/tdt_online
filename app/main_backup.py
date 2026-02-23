import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from app.database import SessionLocal
from app.database_utils import check_and_create_external_images_table

# Configure logger
logger = logging.getLogger("api")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan контекст для инициализации при запуске приложения
    """
    # Startup
    logger.info("Запуск приложения FastAPI...")
    
    # Проверяем и создаем таблицу для внешних изображений при необходимости
    try:
        db = SessionLocal()
        try:
            if check_and_create_external_images_table(db):
                logger.info("Таблица для внешних изображений готова к работе")
            else:
                logger.warning("Не удалось проверить/создать таблицу для внешних изображений")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Ошибка при инициализации таблицы: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Остановка приложения FastAPI...")

app = FastAPI(lifespan=lifespan)

# Configure templates
templates = Jinja2Templates(directory="app/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def read_root(request: Request):
    return {"message": "FastAPI сервер работает!"}

# Подключаем все роутеры
from app.routers import (
    users, 
    modelgoods,
    modelgoods_description, 
    products, 
    modelgoods_search, 
    modelgoods_parameters, 
    ozon_categories, 
    modelgoods_images,
    modelgoods_external_images
)

# Роутеры без префикса /api в своем определении
app.include_router(users.router, prefix="/api")
app.include_router(modelgoods.router, prefix="/api")
app.include_router(modelgoods_description.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(modelgoods_search.router, prefix="/api")
app.include_router(modelgoods_parameters.router, prefix="/api")
app.include_router(ozon_categories.router, prefix="/api")
app.include_router(modelgoods_images.router, prefix="/api")

# Роутер modelgoods_external_images уже имеет префикс /api в своем определении
app.include_router(modelgoods_external_images.router)