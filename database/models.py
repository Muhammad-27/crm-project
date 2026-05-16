from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

# 1. GURUHLAR JADVALI
class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, index=True)  # Qaysi o'qituvchiga tegishli
    name = Column(String, nullable=False)    # Guruh nomi (masalan: IELTS 14:00)
    price = Column(Integer, default=0)       # Oylik to'lov
    
    # Bitta guruhda ko'plab o'quvchilar bo'ladi. (Agar guruh o'chsa, ichidagi o'quvchilar ham o'chadi)
    students = relationship("Student", back_populates="group", cascade="all, delete-orphan")

# 2. O'QUVCHILAR JADVALI
class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, index=True)
    
    # MUHIM: Bu o'quvchi qaysi guruhga tegishli ekanligini bildiruvchi "Kishan"
    group_id = Column(Integer, ForeignKey("groups.id")) 
    
    name = Column(String, nullable=False)
    phone = Column(String)
    fee = Column(Integer, default=0)
    isPaid = Column(Boolean, default=False)
    
    # O'quvchi bitta guruhga tegishli bo'ladi
    group = relationship("Group", back_populates="students")    