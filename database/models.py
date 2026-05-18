from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

# ==========================================
# 1. O'QITUVCHILAR JADVALI (YANGI)
# ==========================================
class Teacher(Base):
    __tablename__ = "center_teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    telegram_id = Column(String, unique=True, index=True, nullable=True) # Keyinchalik bot orqali kirishi uchun
    
    # O'qituvchining guruhlari
    groups = relationship("Group", back_populates="teacher", cascade="all, delete-orphan")

# ==========================================
# 2. GURUHLAR JADVALI
# ==========================================
class Group(Base):
    __tablename__ = "center_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("center_teachers.id")) # YANGILIK: O'qituvchiga bog'landi
    name = Column(String, nullable=False)
    price = Column(Integer, default=0)
    
    teacher = relationship("Teacher", back_populates="groups")
    students = relationship("Student", back_populates="group", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="group", cascade="all, delete-orphan")

# ==========================================
# 3. O'QUVCHILAR JADVALI
# ==========================================
class Student(Base):
    __tablename__ = "center_students"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("center_groups.id")) 
    name = Column(String, nullable=False)
    phone = Column(String)
    fee = Column(Integer, default=0)
    isPaid = Column(Boolean, default=False)
    
    group = relationship("Group", back_populates="students")
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")

# ==========================================
# 4. DAVOMAT JADVALI
# ==========================================
class Attendance(Base):
    __tablename__ = "center_attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("center_students.id"))
    group_id = Column(Integer, ForeignKey("center_groups.id")) 
    date = Column(String, index=True)                    
    is_present = Column(Boolean, default=False)          
    
    student = relationship("Student", back_populates="attendances")
    group = relationship("Group", back_populates="attendances")