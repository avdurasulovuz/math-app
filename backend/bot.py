import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import TELEGRAM_BOT_TOKEN, WEBAPP_URL

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    args = message.text.split()[1] if len(message.text.split()) > 1 else ""
    
    welcome_text = (
        f"Assalomu alaykum, {message.from_user.first_name}! 👋\n\n"
        "Men **Mathy** — sening shaxsiy sun'iy intellekt matematika repetitoringman! 📐✨\n\n"
        "🚀 **Imkoniyatlar:**\n"
        "• 📸 Masalani rasmga ol — ovozli va doskada tushuntiraman!\n"
        "• 🧠 AI Tyutor bilan bevosita muloqot qil\n"
        "• 📚 1-11 sinf darsliklari va formulalar spravochnigi\n"
        "• ⚔️ Do'stlar bilan 1v1 Telegram jangi o'yna\n\n"
    )

    if args.startswith("duel_"):
        duel_id = args.replace("duel_", "")
        welcome_text += f"⚔️ **Sizni {duel_id}-raqamli jangga taklif qilishdi!**\n"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Mathy Ilovasini Ochish",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚔️ Do'stni jangga chaqirish",
                    url=f"https://t.me/share/url?url=https://t.me/mathy_ai_bot?start=duel_{message.from_user.id}&text=Men%20bilan%20matematika%20jangida%20bellash!"
                )
            ]
        ]
    )

    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@dp.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer(
        "Savol yoki masalalarni yuborish uchun pastdagi 'Mathy Ilovasini Ochish' tugmasini bosing! 📲",
        parse_mode="Markdown"
    )

async def main():
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️ Iltimos, config.py yoki .env faylida TELEGRAM_BOT_TOKEN ni o'rnating!")
    print("🤖 Mathy Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
