# Import all ORM models here so migrations can discover metadata.
from sqlalchemy.orm import sessionmaker, declarative_base
# from app.db.session import SessionLocal
from app.core.database import SessionLocal
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()