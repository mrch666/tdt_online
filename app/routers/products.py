from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import logging
import json
import os

from app.schemas.products import ProductResponse
from app.database import get_db

logger = logging.getLogger("api")
router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    desc_path = os.path.join(os.getenv('BASE_DIR'), os.getenv('DESC_SUBDIR'))
    try:
        query = text("""
            SELECT FIRST 50
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
            WHERE FBFILEEXISTS(:path || dec64i0(mg."id") || '_' || dec64i1(mg."id") || '.dat')=0
            GROUP BY mg."id", mg."name", 
                (dec64i0(mg."id") || '_' || dec64i1(mg."id") || '.' || mg."imgext"),
                v."barcode", v."codemodel", v."kmin", vl."name", mg."wlink"
            ORDER BY MAX(mg."changedate") DESC
        """)
        db_result = db.execute(query,
        {
            "path": desc_path
            
        })
        result = list(db_result)
        db_result.close()

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

        return [ProductResponse(**item) for item in raw_data]
    except Exception as e:
        logger.error(f"Products error: {str(e)}")
        raise HTTPException(500, detail=str(e))
