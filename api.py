from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import database.models as models
from database.db import get_db, engine

from typing import List # Tepadagi importlarga shuni qo'shing (agar yo'q bo'lsa)

# --- MA'LUMOTLAR QOLIP (SCHEMAS) --- qismiga shuni qo'shing:
class AttendanceCreate(BaseModel):
    group_id: int
    date: str
    present_ids: List[int]  # Frontend'dan keladigan kelgan o'quvchilar ID lari ro'yxati

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

# --- MA'LUMOTLAR QOLIP (SCHEMAS) ---
class GroupCreate(BaseModel):
    teacher_id: str
    name: str
    price: int

class StudentCreate(BaseModel):
    teacher_id: str
    group_id: int  # Endi o'quvchi qaysi guruhga kirishini aytishimiz shart
    name: str
    phone: str
    fee: int

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
def get_groups(teacher_id: str, db: Session = Depends(get_db)):
    # O'qituvchining barcha guruhlarini topamiz
    groups = db.query(models.Group).filter(models.Group.teacher_id == teacher_id).all()
    
    result = []
    for g in groups:
        # Frontend UI uchun srazu hisob-kitob qilib beramiz:
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
    
    # Guruh o'chirilganda, bazadagi ulanish (cascade) orqali 
    # ichidagi o'quvchilar va ularning davomatlari ham avtomat o'chib ketadi.
    db.delete(group)
    db.commit()
    return {"message": "Guruh muvaffaqiyatli o'chirildi!"}

# ==========================================
# 2. O'QUVCHILAR UCHUN API'LAR
# ==========================================

@app.post("/add-student")
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = models.Student(
        teacher_id=student.teacher_id,
        group_id=student.group_id,
        name=student.name,
        phone=student.phone,
        fee=student.fee
    )
    db.add(new_student)
    db.commit()
    return {"message": "O'quvchi qo'shildi!"}

@app.get("/get-students/{group_id}")
def get_students(group_id: int, db: Session = Depends(get_db)):
    # Endi o'quvchilarni o'qituvchi ID si bilan emas, Guruh ID si bilan tortamiz
    students = db.query(models.Student).filter(models.Student.group_id == group_id).all()
    return students

@app.put("/pay/{student_id}")
def pay_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Topilmadi")
    student.isPaid = True
    db.commit()
    return {"message": "To'lov qabul qilindi"}

@app.delete("/delete-student/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Topilmadi")
    db.delete(student)
    db.commit()
    return {"message": "O'chirildi"}

# ==========================================
# 3. DAVOMAT UCHUN API'LAR
# ==========================================

@app.post("/save-attendance")
def save_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    # 1. Shu guruhdagi barcha o'quvchilarni bazadan olamiz
    students = db.query(models.Student).filter(models.Student.group_id == data.group_id).all()
    
    # 2. Xavfsizlik: Agar o'qituvchi bitta sanada 2 marta davomat jo'natsa, eskisini o'chirib yangilaymiz
    db.query(models.Attendance).filter(
        models.Attendance.group_id == data.group_id,
        models.Attendance.date == data.date
    ).delete()
    
    # 3. Har bir o'quvchi uchun davomatni yozib chiqamiz
    for student in students:
        # Agar o'quvchining ID si 'present_ids' ro'yxatida bo'lsa, demak u kelgan (True)
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
    # Shu guruhning, aniq shu sanadagi faqat "Kelgan" (True) o'quvchilarini topamiz
    records = db.query(models.Attendance).filter(
        models.Attendance.group_id == group_id,
        models.Attendance.date == date,
        models.Attendance.is_present == True
    ).all()
    
    # Faqat o'quvchilarning ID larini ro'yxat qilib jo'natamiz (Masalan: [1, 4, 5])
    present_ids = [record.student_id for record in records]
    return present_ids