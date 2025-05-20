from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Storage, Modelgoods,Folders
from app.routers import modelgoods_parameters
import os

app = FastAPI()

# Configure templates
templates = Jinja2Templates(directory="app/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API routers
app.include_router(modelgoods_parameters.router, prefix="/api")

@app.get("/")
async def read_root(
    request: Request, 
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 10
):
    # Calculate pagination offsets
    total_items = db.query(Storage).count()
    total_pages = (total_items + per_page - 1) // per_page
    
    # Get paginated results
    inventory = db.query(Storage, Modelgoods)\
        .join(Modelgoods, Storage.modelid == Modelgoods.id)\
        .join(Folders, Storage.folderid == Folders.id)\
        .filter(Folders.istrailer == 0)\
        .order_by(Modelgoods.name)\
        .offset((page-1)*per_page)\
        .limit(per_page)\
        .add_columns(
            Modelgoods.name.label('model_name'),
            Folders.name.label('folders_name'),
            Storage.count
        )\
        .all()

    return templates.TemplateResponse("base.html", {
        "request": request,
        "inventory_data": inventory,
        "current_page": page,
        "total_pages": total_pages,
        "per_page": per_page
    })

@app.get("/web/modelgoods/parameters")
async def show_parameters_interface(request: Request):
    return templates.TemplateResponse(
        "endpoints/modelgoods_parameters.html", 
        {"request": request}
    )

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def perform_login(request: Request):
    form_data = await request.form()
    from app.database import get_db
    from sqlalchemy.exc import SQLAlchemyError
    from app.models import Users
    
    db = next(get_db())
    try:
        user = db.query(Users).filter(
            Users.username == form_data["username"],
            Users.password == form_data["password"]  # В реальном проекте используйте хеширование!
        ).first()
        
        if not user:
            return templates.TemplateResponse("login.html", 
                {"request": request, "error": "Неверные учетные данные"},
                status_code=status.HTTP_401_UNAUTHORIZED)
            
        # TODO: Добавить систему сессий/JWT
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="user", value=user.username)
        return response
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {str(e)}")
        return templates.TemplateResponse("login.html", 
            {"request": request, "error": "Ошибка сервера"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
