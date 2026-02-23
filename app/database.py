from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging
import os

load_dotenv()
db_logger = logging.getLogger("database")
db_logger.addHandler(logging.FileHandler("sql.log"))

# Connection string for Firebird
SQLALCHEMY_DATABASE_URL = (
    f"firebird+fdb://"
    f"{os.getenv('FIREBIRD_USER', 'SYSDBA')}:{os.getenv('FIREBIRD_PASSWORD', 'masterkey')}@"
    f"{os.getenv('FIREBIRD_HOST', 'localhost')}:{os.getenv('FIREBIRD_PORT', 3055)}/"
    f"{os.getenv('BASE_DIR')}/{os.getenv('DATABASE_NAME')}"
)

# Create synchronous engine with optimized connection pool
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "fb_library_name": os.getenv('FBCLIENT_PATH', 'C:\\Program Files (x86)\\tdt3\\fbclient.dll'),
        "charset": "WIN1251"
    },
    pool_size=50,           # Увеличить размер пула для высокой нагрузки
    max_overflow=100,       # Увеличить максимальное переполнение
    pool_timeout=30,        # Таймаут соединения 30 секунд
    pool_recycle=1800,      # Пересоздавать соединения каждые 30 минут
    pool_pre_ping=True,     # Проверять соединение перед использованием
    echo_pool=False,        # Логировать операции с пулом (False в продакшене)
)

# Configure session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Synchronous database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
