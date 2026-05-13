from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, User

# SQLite bazasiga ulanish
DATABASE_URL = "postgresql://neondb_owner:npg_10iSmGkcRNhy@ep-broad-morning-aqv7h72d-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(URL_DATABASE, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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