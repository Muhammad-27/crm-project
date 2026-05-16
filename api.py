from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

# O'zingizning fayllaringizdan chaqirib olamiz (AYNAN SHU YER TUSHIB QOLGAN EDI)
from database.db import SessionLocal, engine
from database.models import Student, Base

# Jadvallarni bazada yaratish
Base.metadata.create_all(bind=engine)
# ... (eng tepadagi importlar o'z o'rnida qoladi) ...

app = FastAPI()

# Ruxsat etilgan manzillar ro'yxati (Ham Vercel, ham o'zingizning kompyuteringiz)
origins = [
    "https://crm-rysx.vercel.app",
    "http://localhost:5173"
]

# 1. Odatiy CORS (Xavfsizlik uchun)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. MAJBURIY CORS (Endi kelgan mehmonga qarab ruxsat beradi)
@app.middleware("http")
async def force_cors(request: Request, call_next):
    response = await call_next(request)
    origin = request.headers.get("origin")
    
    # Agar so'rov biz tanigan joylardan kelsa, o'shanga ruxsat beramiz
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = origins[0]
        
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# ... (Pastdagi barcha API funksiyalar: get_db, add_student va boshqalar o'z holicha qoladi) ...

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

class StudentUpdate(BaseModel):
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
    result = []
    for s in students:
        result.append({
            "id": s.id,
            "name": s.full_name,
            "phone": s.phone,
            "isPaid": s.is_paid,
            "fee": s.fee,
            "avatar": f"https://xsgames.co/randomusers/avatar.php?g=pixel&key={s.id}"
        })
    return result

# 3. O'quvchi to'lovini qabul qilish API'si (PUT)
@app.put("/pay/{student_id}")
def receive_payment(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return {"status": "error", "message": "O'quvchi topilmadi!"}
    student.is_paid = True
    db.commit() 
    return {"status": "success", "message": "To'lov qabul qilindi!"}

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