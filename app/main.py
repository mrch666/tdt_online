from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import engine, get_db, Base
from app.models import Vollink, Vol, Storage, Folders, Users, Modelgoods
from contextlib import asynccontextmanager
from typing import List
import logging
import os
import json
import time

from app.routers import users, modelgoods, products, modelgoods_images, modelgoods_description

# Настройка продвинутого логирования
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format='%(asctime)s.%(msecs)03d | %(levelname)-8s | %(module)-15s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup - creating database tables")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

# Подключаем роутеры
app.include_router(users.router)
app.include_router(modelgoods.router)
app.include_router(products.router)
app.include_router(modelgoods_images.router)
app.include_router(modelgoods_description.router)

# Мидлварь для логирования
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"→ {request.method} {request.url.path} [Client: {request.client.host}]")
    start_time = time.time()
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"! Request failed: {str(e)}", exc_info=True)
        raise
    
    process_time = (time.time() - start_time) * 1000
    logger.debug(f"← {response.status_code} | Time: {process_time:.2f}ms | Size: {response.headers.get('content-length', '?')}b")
    
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response

# Healthcheck endpoint
@app.get("/healthcheck")
def healthcheck(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1 FROM RDB$DATABASE"))
        logger.info("Database health check successful")
        return {"status": "ok", "db_connection": "success"}
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return {"status": "error", "db_connection": "failed", "error": str(e)}
