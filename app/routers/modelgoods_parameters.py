from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import os
from typing import Dict, Any
from app.database import get_db
from app.models import dec64i0, dec64i1

router = APIRouter(prefix="/modelgoods/parameters", tags=["modelgoods"])

@router.post("/{model_id}")
async def save_parameters(model_id: str, params: Dict[Any, Any], db: Session = Depends(get_db)):
    try:
        file_path = (
            f"{os.getenv('BASE_DIR')}/{os.getenv('PARAMS_SUBDIR')}/"
            f"{dec64i0(model_id)}_{dec64i1(model_id)}.json"
        )
        
        result = db.execute(text("""
            SELECT saveblobtofile(
                :data, 
                :file_path
            ) 
            FROM RDB$DATABASE
        """), {
            "data": json.dumps(params).encode('utf-8'),
            "file_path": file_path
        }).scalar()
        
        if result != 1:
            raise HTTPException(status_code=500, detail="File save failed")
            
        return {"status": "success", "model_id": model_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{model_id}")
async def get_parameters(model_id: str, db: Session = Depends(get_db)):
    try:
        file_path = (
            f"{os.getenv('BASE_DIR')}/{os.getenv('PARAMS_SUBDIR')}/"
            f"{dec64i0(model_id)}_{dec64i1(model_id)}.json"
        )
        
        result = db.execute(text("""
            SELECT loadblobfromfile(:file_path) 
            FROM RDB$DATABASE
        """), {"file_path": file_path}).fetchone()
        
        if not result or not result[0]:
            return {}
            
        return json.loads(result[0])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
