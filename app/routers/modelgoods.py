from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.schemas.modelgoods import ModelgoodsCreate, ModelgoodsResponse
from app.database import get_db
from app.models import Modelgoods

logger = logging.getLogger("api")
router = APIRouter(prefix="/modelgoods", tags=["modelgoods"])

@router.post("/", response_model=ModelgoodsResponse)
def create_modelgoods(modelgoods: ModelgoodsCreate, db: Session = Depends(get_db)):
    db_modelgoods = Modelgoods(**modelgoods.dict())
    db.add(db_modelgoods)
    try:
        db.commit()
        db.refresh(db_modelgoods)
        logger.info(f"Modelgoods created: {db_modelgoods.name}")
    except Exception as e:
        logger.error(f"Modelgoods creation error: {str(e)}")
        db.rollback()
        raise HTTPException(400, detail=str(e))
    return db_modelgoods

@router.get("/", response_model=List[ModelgoodsResponse])
def read_modelgoods(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Modelgoods).offset(skip).limit(limit).all()

@router.get("/{modelgoods_id}", response_model=ModelgoodsResponse)
def read_modelgoods(modelgoods_id: str, db: Session = Depends(get_db)):
    modelgoods = db.query(Modelgoods).filter(Modelgoods.id == modelgoods_id).first()
    if not modelgoods:
        logger.warning(f"Modelgoods {modelgoods_id} not found")
        raise HTTPException(404, detail="Modelgoods not found")
    return modelgoods

@router.put("/{modelgoods_id}", response_model=ModelgoodsResponse)
def update_modelgoods(
    modelgoods_id: str,
    modelgoods: ModelgoodsCreate,
    db: Session = Depends(get_db)
):
    db_modelgoods = db.query(Modelgoods).filter(Modelgoods.id == modelgoods_id).first()
    if not db_modelgoods:
        raise HTTPException(404, detail="Modelgoods not found")
    
    for key, value in modelgoods.dict().items():
        setattr(db_modelgoods, key, value)
    
    try:
        db.commit()
        db.refresh(db_modelgoods)
        logger.info(f"Modelgoods updated: {modelgoods_id}")
    except Exception as e:
        logger.error(f"Error updating modelgoods {modelgoods_id}: {str(e)}")
        db.rollback()
        raise HTTPException(400, detail=str(e))
    return db_modelgoods

@router.delete("/{modelgoods_id}")
def delete_modelgoods(modelgoods_id: str, db: Session = Depends(get_db)):
    modelgoods = db.query(Modelgoods).filter(Modelgoods.id == modelgoods_id).first()
    if not modelgoods:
        raise HTTPException(404, detail="Modelgoods not found")
    
    try:
        db.delete(modelgoods)
        db.commit()
        logger.info(f"Modelgoods deleted: {modelgoods_id}")
    except Exception as e:
        logger.error(f"Error deleting modelgoods {modelgoods_id}: {str(e)}")
        db.rollback()
        raise HTTPException(400, detail=str(e))
    return {"message": "Modelgoods deleted successfully"}
