from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import logging
import json
import os
from functools import lru_cache
from datetime import datetime, timedelta

from app.schemas.products import ProductResponse
from app.database import get_db

logger = logging.getLogger("api")
router = APIRouter(prefix="/products", tags=["products"])

# Простое кэширование для снижения нагрузки на базу данных
class SimpleCache:
    def __init__(self, ttl_seconds=60):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now())
    
    def clear(self):
        self.cache.clear()

# Глобальный кэш для продуктов
products_cache = SimpleCache(ttl_seconds=30)  # 30 секунд TTL

# LRU кэш для часто запрашиваемых данных
@lru_cache(maxsize=128)
def get_cached_products(noimage: bool, cache_key: str):
    """Кэшированная версия получения продуктов (пустая функция, реальная логика в основном методе)"""
    return None


@router.get("/", response_model=List[ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    noimage: bool = False  # необязательный параметр, по умолчанию False
):
    # Генерируем ключ кэша на основе параметров
    cache_key = f"products_{noimage}"
    
    # Пробуем получить данные из кэша
    cached_result = products_cache.get(cache_key)
    if cached_result is not None:
        logger.info(f"Используем кэшированные данные для noimage={noimage}")
        return cached_result
    
    desc_path = os.path.join(os.getenv('BASE_DIR'), os.getenv('DESC_SUBDIR'))
    logger.info(f"desc_path: {str(desc_path)}")
    logger.info(f"Параметр noimage: {noimage}")
    
    try:
        # Базовый запрос без WHERE условия для FBFILEEXISTS
        base_query = """
            SELECT FIRST 100
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
            JOIN "folders" f ON (s."folderid" = f."id" AND f."istrailer" = '0')
        """
        
        # Добавляем WHERE условие только если noimage=False
        if not noimage:
            base_query += """
                WHERE FBFILEEXISTS(:path || '/' || dec64i0(mg."id") || '_' || dec64i1(mg."id") || '.dat') = 0
            """
        if noimage:
            base_query+="""
               WHERE  mg."imgext"='' 
            """
        # Добавляем GROUP BY и ORDER BY
        base_query += """
            GROUP BY mg."id", mg."name", 
                (dec64i0(mg."id") || '_' || dec64i1(mg."id") || '.' || mg."imgext"),
                v."barcode", v."codemodel", v."kmin", vl."name", mg."wlink"
            ORDER BY MAX(mg."changedate") DESC
        """
        
        logger.debug(f"SQL запрос:\n{base_query}")
        
        query = text(base_query)
        
        # Параметры запроса
        query_params = {}
        if not noimage:
            query_params["path"] = desc_path
        
        logger.debug(f"Параметры запроса: {query_params}")
        
        db_result = db.execute(query, query_params)
        result = list(db_result)
        db_result.close()

        logger.info(f"Найдено строк в результате: {len(result)}")
        
        raw_data = []
        for row in result:
            row_dict = {}
            for key, value in row._mapping.items():
                if key == 'price':
                    row_dict[key] = float(value)
                elif key == 'kmin':
                    row_dict[key] = int(value)
                else:
                    row_dict[key] = str(value).strip()
            raw_data.append(row_dict)
        
        if raw_data:
            logger.debug(f"Первые 3 записи результата: {raw_data[:3]}")
        else:
            logger.warning("Результат запроса пустой")
        
        # Преобразуем в объекты ProductResponse
        response_data = [ProductResponse(**item) for item in raw_data]
        
        # Сохраняем в кэш
        products_cache.set(cache_key, response_data)
        logger.info(f"Данные сохранены в кэш для ключа: {cache_key}")
        
        return response_data
    except Exception as e:
        logger.error(f"Products error: {str(e)}", exc_info=True)
        raise HTTPException(500, detail=str(e))
