import logging
from fastapi import FastAPI, Request
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

app = FastAPI()

# Configure templates
templates = Jinja2Templates(directory="app/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def read_root(request: Request):
    return {"message": "FastAPI сервер работает!"}

# Временно отключим сложные роутеры для тестирования
# from app.routers import users, modelgoods_description, products, modelgoods_search, modelgoods_parameters, ozon_categories, modelgoods_images
# app.include_router(users.router, prefix="/api")
# app.include_router(modelgoods_description.router, prefix="/api")
# app.include_router(products.router, prefix="/api")
# app.include_router(modelgoods_search.router, prefix="/api")
# app.include_router(modelgoods_parameters.router, prefix="/api")
# app.include_router(ozon_categories.router, prefix="/api")
# app.include_router(modelgoods_images.router, prefix="/api")