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

# Create synchronous engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "fb_library_name": os.path.join(os.getenv('BASE_DIR'), "fbclient.dll"),
        "charset": "WIN1251"
    }
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
