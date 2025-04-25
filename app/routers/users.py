from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.schemas.users import UserCreate, UserResponse
from app.database import get_db
from app.models import Users

logger = logging.getLogger("api")
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = Users(**user.dict())
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        logger.info(f"User created: {db_user.username}")
    except Exception as e:
        logger.error(f"User creation error: {str(e)}")
        db.rollback()
        raise HTTPException(400, detail=str(e))
    return db_user

@router.get("/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        return db.query(Users).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Users read error: {str(e)}")
        return {"status": "error", "error": str(e)}

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        logger.warning(f"User {user_id} not found")
        raise HTTPException(404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(404, detail="User not found")
    
    for key, value in user.dict().items():
        setattr(db_user, key, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        logger.info(f"User updated: {user_id}")
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        db.rollback()
        raise HTTPException(400, detail=str(e))
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="User not found")
    
    try:
        db.delete(user)
        db.commit()
        logger.info(f"User deleted: {user_id}")
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        db.rollback()
        raise HTTPException(400, detail=str(e))
    return {"message": "User deleted successfully"}
