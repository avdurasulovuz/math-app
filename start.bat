@echo off
chcp 65001 >nul
title Mathy — AI EdTech Startup Server

echo ========================================================
echo       🚀 MATHY — AI FOTO-TYUTOR & EDTECH STARTAP
echo ========================================================
echo.

cd /d "%~dp0backend"

echo [1/3] Kutubxonalarni tekshirish va o'rnatish...
pip install -r requirements.txt

echo.
echo [2/3] Ma'lumotlar bazasini boyitish (Database Seed)...
python seed.py

echo.
echo [3/3] FastAPI va Telegram Mini App serverini ishga tushirish...
echo.
echo 📱 Mini App:   http://localhost:8000
echo 🖥️  Admin Hub:  http://localhost:8000/admin.html
echo 📚 Swagger API: http://localhost:8000/docs
echo.
echo Telegram botni ishga tushirish uchun alohida oynada:
echo cd backend ^&^& python bot.py
echo ========================================================
echo.

start http://localhost:8000
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
