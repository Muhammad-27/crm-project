from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Bazaga ulanish ssilkasi (.env fayldan olinadi)
DATABASE_URL = os.getenv("URL_DATABASE")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# API uchun bazani ochib beruvchi funksiya
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()