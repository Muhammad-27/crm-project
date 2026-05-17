from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

# 1. GURUHLAR JADVALI
class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, default=0)
    
    students = relationship("Student", back_populates="group", cascade="all, delete-orphan")

# 2. O'QUVCHILAR JADVALI
class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, index=True)
    group_id = Column(Integer, ForeignKey("groups.id")) 
    name = Column(String, nullable=False)
    phone = Column(String)
    fee = Column(Integer, default=0)
    isPaid = Column(Boolean, default=False)
    
    group = relationship("Group", back_populates="students")
    
    # YANGILIK: O'quvchining davomat tarixi
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")

# 3. DAVOMAT JADVALI (YANGI)
class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))  # Qidirish oson bo'lishi uchun
    date = Column(String, index=True)                    # Sanani matn ko'rinishida saqlaymiz: "2026-05-17"
    is_present = Column(Boolean, default=False)          # Keldi (True) yoki Kelmadi (False)
    
    student = relationship("Student", back_populates="attendances")