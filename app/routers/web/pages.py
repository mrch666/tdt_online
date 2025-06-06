from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db
from app.models import Users, Storage, Modelgoods, Folders
from sqlalchemy import cast, String, text, bindparam
import logging

router = APIRouter(prefix="/web")
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)

@router.get("/modelgoods/{modelgoods_id}/details")
async def modelgoods_details(
    request: Request, 
    modelgoods_id: str,
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching modelgoods details for ID: {modelgoods_id}")
    
    try:
        logger.info(f"Searching for modelgoods with ID: '{modelgoods_id}'")
        modelgoods = db.query(Modelgoods).filter(Modelgoods.id.ilike(modelgoods_id)).first()
        
        if modelgoods:
            logger.info(f"Found modelgoods: ID={modelgoods.id}, Name={modelgoods.name}")
        else:
            logger.warning(f"No modelgoods found for ID: '{modelgoods_id}'")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    if not modelgoods:
        logger.warning(f"Modelgoods not found for ID: {modelgoods_id}")
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Проверяем, является ли запрос HTMX-запросом
    is_htmx = request.headers.get("HX-Request") == "true"
    logger.info(f"HTMX request: {is_htmx}")
    
    if is_htmx:
        # Для HTMX-запросов возвращаем только фрагмент
        return templates.TemplateResponse(
            "endpoints/modelgoods_details_fragment.html",
            {
                "request": request,
                "modelgoods": modelgoods,
                "description": modelgoods.comment if modelgoods and modelgoods.comment else ""
            }
        )
    else:
        # Для обычных запросов возвращаем полную страницу
        return templates.TemplateResponse(
            "endpoints/modelgoods_details.html",
            {
                "request": request,
                "current_page": 1,
                "total_pages": 1,
                "modelgoods": modelgoods,
                "description": modelgoods.comment if modelgoods and modelgoods.comment else ""
            }
        )

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "current_page": 1,
        "total_pages": 1
    })

@router.post("/login")
async def perform_login(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    try:
        username = form_data["username"].strip()
        password = form_data["password"].strip()
        logger.info(f"Attempting login with credentials: {username}/{password}")
        
        user = db.query(Users).filter(
            cast(Users.username, String).ilike(username),
            cast(Users.password, String).ilike(password)
        ).first()
        
        logger.info(f"Found user: {user.username if user else None}")
        
        if not user:
            return templates.TemplateResponse("login.html", 
                {"request": request, "error": "Неверные учетные данные", "current_page": 1, "total_pages": 1},
                status_code=status.HTTP_401_UNAUTHORIZED)
            
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="user", value=user.username)
        return response
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {str(e)}")
        return templates.TemplateResponse("login.html", 
            {"request": request, "error": "Ошибка сервера", "current_page": 1, "total_pages": 1},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
