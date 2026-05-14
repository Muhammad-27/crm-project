from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

# O'zingizning fayllaringizdan chaqirib olamiz
from database.db import SessionLocal, engine
from database.models import Student, Base

# Jadvallarni bazada yaratish (Agar yo'q bo'lsa, o'zi ochadi)
Base.metadata.create_all(bind=engine)

app = FastAPI()


# ... qolgan kodlar o'zgarishsiz qoladi ...

# React ruxsatsiz bloklanib qolmasligi uchun CORS sozlamasi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://crm-rysx.vercel.app"], # DING! Yangi Vercel manzil. Oxirida "/" bo'lmasin!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Baza bilan bog'lanish funksiyasi
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# React'dan keladigan o'quvchi ma'lumotlari qolipi (Pydantic model)
class StudentCreate(BaseModel):
    teacher_id: str
    name: str
    phone: str
    fee: int

# 1. Yangi o'quvchi qo'shish API'si (POST)
@app.post("/add-student")
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = Student(
        teacher_telegram_id=student.teacher_id,
        full_name=student.name,
        phone=student.phone,
        fee=student.fee,
        is_paid=False
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {"status": "success", "message": "O'quvchi saqlandi!", "student": new_student}

# 2. O'qituvchining o'quvchilarini tortib olish API'si (GET)
@app.get("/get-students/{teacher_id}")
def get_students(teacher_id: str, db: Session = Depends(get_db)):
    students = db.query(Student).filter(Student.teacher_telegram_id == teacher_id).all()
    # Ma'lumotlarni React tushunadigan shaklda qaytaramiz
    result = []
    for s in students:
        result.append({
            "id": s.id,
            "name": s.full_name,
            "phone": s.phone,
            "isPaid": s.is_paid,
            "fee": s.fee,
            "avatar": f"https://xsgames.co/randomusers/avatar.php?g=pixel&key={s.id}" # Vaqtinchalik avatar
        })
    return result
# 3. O'quvchi to'lovini qabul qilish API'si (PUT)
@app.put("/pay/{student_id}")
def receive_payment(student_id: int, db: Session = Depends(get_db)):
    # Bazadan ID bo'yicha o'quvchini qidirib topamiz
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        return {"status": "error", "message": "O'quvchi topilmadi!"}
    
    # O'quvchining qarzini "To'ladi" (True) ga o'zgartiramiz
    student.is_paid = True
    db.commit() # O'zgarishni bazaga saqlaymiz
    
    return {"status": "success", "message": "To'lov qabul qilindi!"}
# Tahrirlash uchun ma'lumot qolipi
class StudentUpdate(BaseModel):
    name: str
    phone: str
    fee: int

# 4. Tahrirlash (Edit) API'si
@app.put("/edit-student/{student_id}")
def edit_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return {"status": "error", "message": "O'quvchi topilmadi!"}
    
    student.full_name = data.name
    student.phone = data.phone
    student.fee = data.fee
    db.commit()
    return {"status": "success", "message": "Ma'lumot yangilandi!"}

# 5. O'chirish (Delete) API'si
@app.delete("/delete-student/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
    return {"status": "success", "message": "O'quvchi o'chirildi!"}