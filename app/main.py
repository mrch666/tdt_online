import logging
from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Configure logger
logger = logging.getLogger("api")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
from sqlalchemy.orm import joinedload
from app.database import SessionLocal
from sqlalchemy import cast, String, text, bindparam, select, func
from app.database import get_db
from app.models import Storage, Modelgoods,Folders
from app.routers import users, modelgoods_description, products, modelgoods_search, modelgoods_parameters
import os

app = FastAPI()

# Configure templates
templates = Jinja2Templates(directory="app/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API routers
app.include_router(users.router, prefix="/api")
app.include_router(modelgoods_description.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(modelgoods_search.router, prefix="/api")
app.include_router(modelgoods_parameters.router, prefix="/api")

@app.get("/")
def read_root(
    request: Request, 
    page: int = 1,
    per_page: int = 10,
    search: str = None
):
    with SessionLocal() as db:
        # Base query with relationships
        query = select(Storage)\
            .options(
                joinedload(Storage.modelgoods),
                joinedload(Storage.folder)
            )\
            .join(Folders, Storage.folderid == Folders.id)\
            .join(Modelgoods, Storage.modelid == Modelgoods.id)\
            .where(Folders.istrailer == 0)
        
        if search:
            search_terms = search.split()
            for term in search_terms:
                query = query.where(Modelgoods.name.ilike(f"%{term}%"))
        
        # Get total count and pagination
        total_items = db.scalar(select(func.count()).select_from(query.subquery()))
        total_pages = (total_items + per_page - 1) // per_page
        
        # Paginated results
        result = db.execute(
            query.order_by(Modelgoods.name)
                .offset((page-1)*per_page)
                .limit(per_page)
        )
        inventory = result.unique().scalars().all()

    return templates.TemplateResponse("home.html", {
        "request": request,
        "inventory_data": inventory,
        "current_page": page,
        "total_pages": total_pages,
        "per_page": per_page
    })

from app.routers.web import pages as web_pages

# Подключаем веб-роуты
app.include_router(web_pages.router, prefix="/web")
