from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import database.models as models
from database.db import get_db, engine

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