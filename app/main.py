from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import engine, get_db, Base
from app.models import Modelgoods, Users, Vollink, Vol, Storage, Folders  # Добавляем Users
from contextlib import asynccontextmanager
from typing import List
from pydantic import BaseModel
import logging
import os
import json

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

# Схемы для Modelgoods
class ModelgoodsCreate(BaseModel):
    typeid: str
    firmaid: str
    name: str
    userid: str

class ModelgoodsResponse(ModelgoodsCreate):
    id: str
    class Config:
        orm_mode = True

# Схемы для Users
class UserCreate(BaseModel):
    username: str
    password: str
    peopleid: str
    rangid: str

class UserResponse(UserCreate):
    id: str
    class Config:
        orm_mode = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup - creating database tables")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

import time  # Добавляем импорт модуля времени

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

# Эндпоинты для Users
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = Users(**user.dict())
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        logger.info(f"User created successfully: {db_user.username}")
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_user

@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
       return db.query(Users).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Users  error: {str(e)}")
        return {"status": "error", "Users": "failed", "error": str(e)}



@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User retrieved: {user_id}")
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user.dict().items():
        setattr(db_user, key, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        logger.info(f"User updated: {user_id}")
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        db.delete(user)
        db.commit()
        logger.info(f"User deleted: {user_id}")
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "User deleted successfully"}

# Эндпоинты для Modelgoods
@app.post("/modelgoods/", response_model=ModelgoodsResponse)
def create_modelgoods(modelgoods: ModelgoodsCreate, db: Session = Depends(get_db)):
    db_modelgoods = Modelgoods(**modelgoods.dict())
    db.add(db_modelgoods)
    try:
        db.commit()
        db.refresh(db_modelgoods)
        logger.info(f"Modelgoods created: {db_modelgoods.name}")
    except Exception as e:
        logger.error(f"Error creating modelgoods: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_modelgoods

@app.get("/modelgoods/", response_model=List[ModelgoodsResponse])
def read_modelgoods(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Modelgoods).offset(skip).limit(limit).all()

@app.get("/modelgoods/{modelgoods_id}", response_model=ModelgoodsResponse)
def read_modelgoods(modelgoods_id: str, db: Session = Depends(get_db)):
    modelgoods = db.query(Modelgoods).filter(Modelgoods.id == modelgoods_id).first()
    if not modelgoods:
        logger.warning(f"Modelgoods not found: {modelgoods_id}")
        raise HTTPException(status_code=404, detail="Modelgoods not found")
    logger.info(f"Modelgoods retrieved: {modelgoods_id}")
    return modelgoods

@app.put("/modelgoods/{modelgoods_id}", response_model=ModelgoodsResponse)
def update_modelgoods(
    modelgoods_id: str,
    modelgoods: ModelgoodsCreate,
    db: Session = Depends(get_db)
):
    db_modelgoods = db.query(Modelgoods).filter(Modelgoods.id == modelgoods_id).first()
    if not db_modelgoods:
        raise HTTPException(status_code=404, detail="Modelgoods not found")
    
    for key, value in modelgoods.dict().items():
        setattr(db_modelgoods, key, value)
    
    try:
        db.commit()
        db.refresh(db_modelgoods)
        logger.info(f"Modelgoods updated: {modelgoods_id}")
    except Exception as e:
        logger.error(f"Error updating modelgoods {modelgoods_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_modelgoods

@app.delete("/modelgoods/{modelgoods_id}")
def delete_modelgoods(modelgoods_id: str, db: Session = Depends(get_db)):
    modelgoods = db.query(Modelgoods).filter(Modelgoods.id == modelgoods_id).first()
    if not modelgoods:
        raise HTTPException(status_code=404, detail="Modelgoods not found")
    
    try:
        db.delete(modelgoods)
        db.commit()
        logger.info(f"Modelgoods deleted: {modelgoods_id}")
    except Exception as e:
        logger.error(f"Error deleting modelgoods {modelgoods_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Modelgoods deleted successfully"}

# Новый эндпоинт для сложного SQL-запроса
class ProductResponse(BaseModel):
    modelid: str
    name: str
    scount: str
    image: str
    price: float
    barcode: str
    codemodel: str
    kmin: int
    volname: str
    wlink: str
    cell: str
    
    class Config:
        orm_mode = True
        extra = "allow"  # Разрешаем дополнительные поля во время дебага

@app.get("/products/", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    try:
        query = text("""
           SELECT FIRST 1
    mg."id" AS "modelid",
    mg."name",
    LIST('на складе: ' || f."name" || ' - ' || (s."count"/v."kmin") || ' ' || vl."name" || '
') AS "scount",
    (dec64i0(mg."id") || '_' || dec64i1(mg."id") || '.' || mg."imgext") AS "image",
    MAX(s."p2value") AS price,
    v."barcode",
    v."codemodel",
    v."kmin",
    vl."name" AS volname,
    mg."wlink",
    LIST(s."cell") AS cell
FROM "modelgoods" AS mg
JOIN "vollink" v ON (mg."id" = v."modelid" AND v."level" = 1.0)
JOIN "vol" vl ON (vl."id" = v."vol1id")
JOIN "storage" s ON (s."modelid" = mg."id" AND s."count" > 0.0 AND s."count" IS NOT NULL)
JOIN "folders" f ON (s."folderid" = f."id" AND f."istrailer" = '0'
    --                AND f."id" IN ('0rfarg00002C', '0000010004cx', '0000010004Xu', '0rfarg000b52')
                     )
 and FBFILEEXISTS('C:\Program Files (x86)\\tdt3\\bases\desc\\' || dec64i0(mg."id") || '_' || dec64i1(mg."id") || '.dat')=0 
GROUP BY
    mg."id",
    mg."name",
    dec64i0(mg."id") || '_' || dec64i1(mg."id") || '.' || mg."imgext",
    v."barcode",
    v."codemodel",
    v."kmin",
    vl."name",
    mg."wlink"
ORDER BY MAX(mg."changedate") DESC
        """)
        # Явное управление сессией и результатом
        db_result = db.execute(query)
        result = list(db_result)
        db_result.close()  # Корректное закрытие объекта результата
        # Логируем сырую структуру данных
        if result:
            logger.debug(f"Raw row structure: {result[0]._fields}")
            logger.debug(f"First row sample: {dict(result[0]._mapping)}")
        
        # Явное преобразование с проверкой типов
        raw_data = []
        for row in result:
            # Преобразование с учетом типов данных
            row_dict = {}
            for key, value in row._mapping.items():
                if key == 'price':
                    row_dict[key] = float(value)
                elif key == 'kmin':
                    row_dict[key] = int(value)
                else:
                    if key == "scount":
                        # Усиленная обработка для scount: удаляем все виды пробелов и непечатаемые символы
                        cleaned_parts = []
                        # Разделяем по шаблону ",\n" который используется в SQL-запросе
                        for part in str(value).split(',\n'):
                            # Удаляем все пробелы в начале/конце и заменяем множественные пробелы на один
                            part_clean = ' '.join(part.strip().split())
                            if part_clean:
                                cleaned_parts.append(part_clean)
                        # Собираем строку с нормализованными разделителями
                        row_dict[key] = ', '.join(cleaned_parts)
                    else:
                        row_dict[key] = str(value).strip()  # Обрезаем пробелы для остальных полей
            logger.debug(f"Processed row: {json.dumps(row_dict, indent=2)}")
            raw_data.append(row_dict)
        logger.debug(f"Raw SQL response: {json.dumps(raw_data, indent=2, ensure_ascii=False)}")
        
        # Валидация данных
        validated_data = []
        for item in raw_data:
            try:
                validated = ProductResponse(**item).dict()
                validated_data.append(validated)
            except Exception as e:
                logger.error(f"Validation error for item {item}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Data validation failed: {str(e)}")
        
        return validated_data
    except Exception as e:
        logger.error(f"Products error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/healthcheck")
def healthcheck(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1 FROM RDB$DATABASE"))
        logger.info("Database health check successful")
        return {"status": "ok", "db_connection": "success"}
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return {"status": "error", "db_connection": "failed", "error": str(e)}
