import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from dotenv import load_dotenv

# Bazani ulash
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db import init_db, get_or_create_user, update_user_role

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- TWA (Web App) URL manzili ---
# Hozircha vaqtinchalik havola turadi, React'ni ishga tushirgach buni o'zgartiramiz
WEB_APP_URL = "https://crm-rysx.vercel.app" 

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    user = get_or_create_user(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name
    )
    
    # Web App uchun tugma yaratamiz
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Tizimga kirish (Web App)", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])

    await message.answer(
        f"Assalomu alaykum, {user.full_name}!\n\n"
        f"Siz tizimda <b>{user.role}</b> sifatida ro'yxatdan o'tdingiz. Pastdagi tugma orqali ilovaga kiring:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# Maxfiy buyruq: O'zingizni o'qituvchi (admin) qilish uchun
@dp.message(Command("make_me_teacher"))
async def make_teacher_handler(message: types.Message):
    update_user_role(message.from_user.id, "teacher")
    await message.answer("Tabriklayman! Endi siz tizimda 'teacher' (o'qituvchi) rolidasiz. O'zgarishni ko'rish uchun /start bosing.")

async def main():
    init_db()
    print("Bot ishga tushdi va Baza ulandi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())