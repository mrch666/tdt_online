from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import logging
from app.database import get_db
from app.schemas.modelgoods import StorageSearchResponse

logger = logging.getLogger("api")
router = APIRouter(prefix="/modelgoods/search", tags=["modelgoods"])

@router.get(
    "/",
    response_model=List[StorageSearchResponse],
    summary="Поиск моделей по названию",
    response_description="Список найденных моделей",
    responses={
        200: {"description": "Успешный поиск"},
        500: {"description": "Ошибка сервера"}
    })
def search_models(
    searchtext: str = Query("", description="Текст для поиска"),
    skip: int = Query(0, ge=0, description="Смещение в результатах"),
    limit: int = Query(100, le=500, description="Максимальное количество результатов (до 500)"),
    db: Session = Depends(get_db)
):
    """Поиск моделей товаров по названию (регистронезависимый)"""
    try:
        search_terms = []
        conditions = []
        joins = [
            "JOIN \"vollink\" v ON (mg.\"id\" = v.\"modelid\" AND v.\"level\" = 1.0)",
            "JOIN \"vol\" vl ON (vl.\"id\" = v.\"vol1id\")",
            "JOIN \"storage\" s ON (s.\"modelid\" = mg.\"id\" AND s.\"count\" > 0.0)",
            "JOIN \"folders\" f ON (s.\"folderid\" = f.\"id\" AND f.\"istrailer\" = '0' "
            "AND f.\"id\" IN ('0rfarg00002C', '0000010004cx', '0000010004Xu', '0rfarg000b52'))"
        ]
        
        if searchtext:
            searchtext = searchtext.strip()
            if " " in searchtext:
                for i, term in enumerate(searchtext.split(), 1):
                    conditions.append(f"UPPER(mg.\"name\") CONTAINING :term{i}")
                    search_terms.append(term.upper())
            else:
                conditions.append(f"UPPER(mg.\"name\") CONTAINING :term1")
                search_terms.append(searchtext.upper())
            
            if searchtext.isdigit():
                conditions.append("(v.\"codemodel\" = :code OR v.\"barcode\" = :code)")
                search_terms.append(searchtext)

        sql = text(f"""
            SELECT FIRST :limit SKIP :skip
                mg."id",
                mg."name",
                mg."typeid",
                mg."firmaid",
                mg."userid",
                LIST('на складе: ' || f."name" || ' - ' || (s."count"/v."kmin") || ' ' || vl."name" || '\n') AS count_info,
                dec64i0(mg."id") || '_' || dec64i1(mg."id") || '.' || mg."imgext" AS image,
                MAX(s."p2value") AS price,
                v."barcode",
                v."codemodel",
                v."kmin",
                vl."name" AS volname,
                mg."wlink",
                LIST(s."cell") AS cells
            FROM "modelgoods" mg
            {' '.join(joins)}
            {f'WHERE {" AND ".join(conditions)}' if conditions else ""}
            GROUP BY mg."id", mg."name", mg."typeid", mg."firmaid", mg."userid", 
                     mg."imgext", mg."wlink", v."barcode", v."codemodel", v."kmin", vl."name"
            ORDER BY mg."name"
        """)
        
        params = {
            "limit": limit,
            "skip": skip,
            **{f"term{i}": term for i, term in enumerate(search_terms, 1)},
            **({"code": searchtext} if searchtext.isdigit() else {})
        }

        logger.info("Выполняем SQL-запрос:\n%s\nПараметры: %s", sql, params)
        result = db.execute(sql, params).fetchall()
        
        return [{
            "id": row.id,
            "name": row.name,
            "typeid": row.typeid,
            "firmaid": row.firmaid,
            "userid": row.userid,
            "count": str(row.count_info),
            "image": row.image,
            "price": int(row.price * row.kmin) if row.price else 0,
            "barcode": row.barcode,
            "codemodel": row.codemodel,
            "volname": row.volname,
            "wlink": row.wlink,
            "cell": row.cells
        } for row in result]
            
    except Exception as e:
        logger.error(f"Ошибка поиска: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
