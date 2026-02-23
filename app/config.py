"""
Конфигурация приложения FastAPI
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Настройки приложения"""
    
    # Порт сервера
    SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
    
    # Хост сервера
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    
    # Базовый URL API
    API_BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{SERVER_PORT}")
    
    # Настройки базы данных
    FIREBIRD_USER = os.getenv("FIREBIRD_USER", "SYSDBA")
    FIREBIRD_PASSWORD = os.getenv("FIREBIRD_PASSWORD", "masterkey")
    FIREBIRD_HOST = os.getenv("FIREBIRD_HOST", "localhost")
    FIREBIRD_PORT = int(os.getenv("FIREBIRD_PORT", 3055))
    BASE_DIR = os.getenv("BASE_DIR")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    FBCLIENT_PATH = os.getenv("FBCLIENT_PATH", "C:\\Program Files (x86)\\tdt3\\fbclient.dll")
    
    # Пути для изображений
    IMAGE_UPLOAD_PATH = os.getenv("IMAGE_UPLOAD_PATH", "C:\\Program Files (x86)\\tdt3\\bases\\img")
    
    # Настройки логирования
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_api_url(cls, endpoint: str = "") -> str:
        """
        Получить полный URL для API endpoint
        
        Args:
            endpoint: Путь endpoint (например, "/modelgoods/image/")
            
        Returns:
            Полный URL (например, "http://localhost:8000/modelgoods/image/")
        """
        # Убираем начальный слэш если есть
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return f"{cls.API_BASE_URL}/{endpoint}"
    
    @classmethod
    def get_modelgoods_image_url(cls) -> str:
        """
        Получить URL для загрузки изображений товаров
        """
        return cls.get_api_url("modelgoods/image/")

# Создаем экземпляр настроек
settings = Settings()