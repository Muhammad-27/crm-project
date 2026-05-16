from database.db import engine, Base
import database.models  # Jadvallarni tanib olishi uchun kerak

print("Eski bazani portlatyapmiz... 💣")
Base.metadata.drop_all(bind=engine)
print("Yangi 'Guruhlar' va 'O'quvchilar' bazasini quryapmiz... 🏗️")
Base.metadata.create_all(bind=engine)
print("Tayyor! 🎉 Baza top-toza bo'ldi!")