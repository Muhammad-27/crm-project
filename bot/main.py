import asyncio
import os
import sys
from dotenv import load_dotenv

# 1. .env FAYLNI O'QIYMIZ
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- TWA (Web App) URL manzili ---
WEB_APP_URL = "https://crm-rysx.vercel.app/" 

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    # Web App uchun tugma yaratamiz
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Tizimga kirish (Web App)", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])

    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
        f"EduTrack CRM tizimiga xush kelibsiz. Pastdagi tugma orqali ilovaga kiring:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

async def main():
    print("Bot muvaffaqiyatli ishga tushdi! 🚀 Eshiklar ochiq!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())