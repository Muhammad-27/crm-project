from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import database.models as models
from database.db import get_db, engine
from typing import List

# Bazani tekshirish
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CORS XAVFSIZLIK ---
origins = [
    "https://crm-rysx.vercel.app",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def force_cors(request: Request, call_next):
    response = await call_next(request)
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
    elif origins:
        response.headers["Access-Control-Allow-Origin"] = origins[0]
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.get("/")
def home():
    return {"status": "ok", "message": "Server 24/7 ishlab turibdi! 🚀"}

# ==========================================
# --- MA'LUMOTLAR QOLIP (SCHEMAS) ---
# ==========================================
class TeacherCreate(BaseModel):
    name: str
    phone: str
    telegram_id: str = None

class TeacherUpdate(BaseModel): # <-- MANA BUNI TO'G'IRLADIM (To'g'ri joylashtirildi)
    name: str
    phone: str
    telegram_id: str = None

class GroupCreate(BaseModel):
    teacher_id: int
    name: str
    price: int

class StudentCreate(BaseModel):
    group_id: int
    name: str
    phone: str
    fee: int
    
class StudentUpdate(BaseModel):
    name: str
    phone: str
    fee: int
    
class AttendanceCreate(BaseModel):
    group_id: int
    date: str
    present_ids: List[int] 


# ==========================================
# 0. O'QITUVCHILAR UCHUN API'LAR (ADMIN UCHUN)
# ==========================================

@app.post("/add-teacher")
def add_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    new_teacher = models.Teacher(
        name=teacher.name,
        phone=teacher.phone,
        telegram_id=teacher.telegram_id
    )
    db.add(new_teacher)
    db.commit()
    return {"message": "O'qituvchi muvaffaqiyatli qo'shildi!"}

@app.get("/get-teachers")
def get_teachers(db: Session = Depends(get_db)):
    teachers = db.query(models.Teacher).all()
    result = []
    for t in teachers:
        result.append({
            "id": t.id,
            "name": t.name,
            "phone": t.phone,
            "telegram_id": t.telegram_id, # Frontendda tahrirlash uchun kerak bo'ladi
            "groupCount": len(t.groups)
        })
    return result

@app.put("/edit-teacher/{teacher_id}")
def edit_teacher(teacher_id: int, teacher_data: TeacherUpdate, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Ustoz topilmadi")
    
    teacher.name = teacher_data.name
    teacher.phone = teacher_data.phone
    teacher.telegram_id = teacher_data.telegram_id
    db.commit()
    return {"message": "Ustoz ma'lumotlari yangilandi! ✏️"}

@app.delete("/delete-teacher/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Ustoz topilmadi")
    
    db.delete(teacher)
    db.commit()
    return {"message": "Ustoz muvaffaqiyatli o'chirildi! 🗑️"}


# ==========================================
# 1. GURUHLAR UCHUN API'LAR
# ==========================================

@app.post("/add-group")
def add_group(group: GroupCreate, db: Session = Depends(get_db)):
    new_group = models.Group(
        teacher_id=group.teacher_id, 
        name=group.name,
        price=group.price
    )
    db.add(new_group)
    db.commit()
    return {"message": "Guruh muvaffaqiyatli qo'shildi!"}

@app.get("/get-groups/{teacher_id}")
def get_groups(teacher_id: int, db: Session = Depends(get_db)): 
    groups = db.query(models.Group).filter(models.Group.teacher_id == teacher_id).all()
    result = []
    for g in groups:
        student_count = len(g.students)
        expected_revenue = sum([s.fee for s in g.students])
        result.append({
            "id": g.id,
            "name": g.name,
            "price": g.price,
            "studentCount": student_count,
            "expectedRevenue": expected_revenue
        })
    return result

@app.delete("/delete-group/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")
    
    db.delete(group)
    db.commit()
    return {"message": "Guruh muvaffaqiyatli o'chirildi!"}


# ==========================================
# 2. O'QUVCHILAR UCHUN API'LAR
# ==========================================

@app.post("/add-student")
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = models.Student(
        group_id=student.group_id, 
        name=student.name,
        phone=student.phone,
        fee=student.fee
    )
    db.add(new_student)
    db.commit()
    return {"message": "O'quvchi muvaffaqiyatli qo'shildi!"}

@app.get("/get-students/{group_id}")
def get_students(group_id: int, db: Session = Depends(get_db)):
    students = db.query(models.Student).filter(models.Student.group_id == group_id).all()
    result = []
    for s in students:
        result.append({
            "id": s.id,
            "name": s.name,
            "phone": s.phone,
            "fee": s.fee,
            "isPaid": s.isPaid
        })
    return result

@app.put("/edit-student/{student_id}")
def edit_student(student_id: int, student_data: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")
    student.name = student_data.name
    student.phone = student_data.phone
    student.fee = student_data.fee
    db.commit()
    return {"message": "O'quvchi ma'lumotlari yangilandi! ✏️"}

@app.put("/pay-student/{student_id}")
def pay_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")
    student.isPaid = not student.isPaid
    db.commit()
    return {"message": "To'lov holati o'zgardi! 💸"}

@app.delete("/delete-student/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
        return {"message": "O'quvchi o'chirildi"}
    raise HTTPException(status_code=404, detail="O'quvchi topilmadi")


# ==========================================
# 3. DAVOMAT UCHUN API'LAR
# ==========================================

@app.post("/save-attendance")
def save_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    students = db.query(models.Student).filter(models.Student.group_id == data.group_id).all()
    
    db.query(models.Attendance).filter(
        models.Attendance.group_id == data.group_id,
        models.Attendance.date == data.date
    ).delete()
    
    for student in students:
        is_present = student.id in data.present_ids
        new_record = models.Attendance(
            student_id=student.id,
            group_id=data.group_id,
            date=data.date,
            is_present=is_present
        )
        db.add(new_record)
        
    db.commit()
    return {"message": "Davomat muvaffaqiyatli saqlandi!"}

@app.get("/get-attendance/{group_id}")
def get_attendance(group_id: int, date: str, db: Session = Depends(get_db)):
    records = db.query(models.Attendance).filter(
        models.Attendance.group_id == group_id,
        models.Attendance.date == date,
        models.Attendance.is_present == True
    ).all()
    present_ids = [record.student_id for record in records]
    return present_ids

@app.get("/student-history/{student_id}")
def get_student_history(student_id: int, db: Session = Depends(get_db)):
    history = db.query(models.Attendance).filter(
        models.Attendance.student_id == student_id
    ).order_by(models.Attendance.date.desc()).all()
    result = []
    for h in history:
        result.append({
            "date": h.date,
            "isPresent": h.is_present
        })
    return result

@app.get("/group-attendance-dates/{group_id}")
def get_group_attendance_dates(group_id: int, db: Session = Depends(get_db)):
    records = db.query(models.Attendance.date).filter(
        models.Attendance.group_id == group_id
    ).distinct().order_by(models.Attendance.date.desc()).all()
    dates = [r[0] for r in records]
    return dates