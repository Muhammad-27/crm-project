import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# (Agar oldindan User modelini chaqirgan bo'lsangiz, u shu yerda tursin)
from database.models import User 

# 1. Kompyuterda ishlaganda .env ni o'qiydi, Render'da esa o'z xotirasidan oladi
load_dotenv()

URL_DATABASE = os.getenv("URL_DATABASE")

# 2. Baza bilan ulanish (PostgreSQL)
engine = create_engine(URL_DATABASE, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Pastdagi funksiyalaringiz o'zgarishsiz qoladi ---

def init_db():
    # Jadvallarni yaratish
    Base.metadata.create_all(bind=engine)

def get_or_create_user(telegram_id: str, full_name: str):
    # Foydalanuvchi bazada bormi tekshiradi, yo'q bo'lsa qo'shadi
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
    
    if not user:
        user = User(telegram_id=str(telegram_id), full_name=full_name, role="student")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    db.close()
    return user

def update_user_role(telegram_id: str, new_role: str):
    # Foydalanuvchi rolini o'zgartirish funksiyasi
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
    if user:
        user.role = new_role
        db.commit()
    db.close()
    return True