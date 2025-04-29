from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import os
import json
import tempfile
import zipfile

from app.database import get_db

logger = logging.getLogger("api")
router = APIRouter(prefix="/modelgoods/image", tags=["modelgoods_images"])

@router.post("/")
async def upload_model_image(
    modelid: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        imgext = file.filename.split('.')[-1].split('?')[0]
        
        result = db.execute(
            text("""
                SELECT FIRST 1 
                    DEC64I0(MG."id") || '_' || DEC64I1(MG."id") || '.' || MG."imgext" 
                FROM "modelgoods" MG 
                WHERE MG."id" = :modelid
            """),
            {"modelid": modelid}
        ).fetchone()
        
        if not result or not result[0]:
            raise HTTPException(404, "Model not found")
            
        filename = result[0].split('?')[0]
        img_path = os.path.join(os.getenv('BASE_DIR'), os.getenv('IMG_SUBDIR'))

        try:
            file_data = await file.read()
            db.execute(
                text("SELECT * FROM wp_SaveBlobToFile(:path, :filename, :data)"),
                {
                    "path": img_path,
                    "filename": filename,
                    "data": file_data
                }
            )
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"File save error: {str(e)}")
            raise HTTPException(500, "File save failed")
        finally:
            await file.close()

        db.execute(
            text("""
                UPDATE modelgoods 
                SET imgext = :imgext, 
                    changedate = CURRENT_TIMESTAMP 
                WHERE id = :modelid
            """),
            {"imgext": imgext, "modelid": modelid}
        )
        db.commit()

        return {"status": "success", "filename": filename}
        
    except Exception as e:
        logger.error(f"Image upload error: {str(e)}")
        raise HTTPException(500, "Internal server error")
