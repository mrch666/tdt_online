from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import os
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from app.database import get_db

logger = logging.getLogger("api")
router = APIRouter(prefix="/ozon/categories", tags=["ozon_categories"])

class CategoryItem(BaseModel):
    category_id: int
    title: str
    children: List['CategoryItem'] = []

CategoryItem.update_forward_refs()

@router.get("/", response_model=List[CategoryItem])
async def get_ozon_categories(
    db: Session = Depends(get_db)
):
    """
    Получение категорий Ozon из JSON файла
    """
    try:
        # Путь к JSON файлу с категориями
        json_path = os.path.join(os.path.dirname(__file__), "web", "ozon_categories.json")
        
        if not os.path.exists(json_path):
            logger.error(f"Файл категорий не найден: {json_path}")
            raise HTTPException(404, "Файл категорий не найден")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
        
        return categories_data
        
    except Exception as e:
        logger.error(f"Ошибка получения категорий Ozon: {str(e)}")
        raise HTTPException(500, "Internal server error")

@router.get("/{category_id}", response_model=CategoryItem)
async def get_ozon_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Получение конкретной категории Ozon по ID
    """
    try:
        json_path = os.path.join(os.path.dirname(__file__), "web", "ozon_categories.json")
        
        if not os.path.exists(json_path):
            raise HTTPException(404, "Файл категорий не найден")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
        
        def find_category(categories, target_id):
            for category in categories:
                if category['category_id'] == target_id:
                    return category
                if 'children' in category:
                    found = find_category(category['children'], target_id)
                    if found:
                        return found
            return None
        
        category = find_category(categories_data, category_id)
        
        if not category:
            raise HTTPException(404, "Категория не найдена")
        
        return category
        
    except Exception as e:
        logger.error(f"Ошибка получения категории Ozon: {str(e)}")
        raise HTTPException(500, "Internal server error")