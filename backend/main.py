from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import random
import json
import os

from database import SessionLocal, init_db, User, Resource, Problem, Duel
from services.ai_service import solve_math_problem, socratic_tutor_chat
from services.parser_service import parse_pdf_textbook

app = FastAPI(title="Mathy API", version="1.0.0", description="Mathy EdTech AI Backend")

# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup va Baza initsializatsiyasi
@app.on_event("startup")
def on_startup():
    init_db()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class ChatRequest(BaseModel):
    message: str
    mode: Optional[str] = "socratic"
    grade: Optional[int] = 7

class ScanTextRequest(BaseModel):
    text: str
    grade: Optional[int] = 7

class UserProgressUpdate(BaseModel):
    telegram_id: int
    coins_delta: int = 0
    xp_delta: int = 0
    increment_streak: bool = False

# ================= REST API ROUTES =================

# 1. Masalani skanerlash va tahlil qilish (Doska rejimi)
@app.post("/api/scan")
async def scan_problem(
    file: Optional[UploadFile] = File(None),
    text_prompt: Optional[str] = Form(None),
    grade: int = Form(7)
):
    image_bytes = None
    if file:
        image_bytes = await file.read()
    
    result = solve_math_problem(image_bytes=image_bytes, text_prompt=text_prompt, grade=grade)
    return result

# 2. Sokratik AI Tyutor bilan suhbat
@app.post("/api/chat")
def chat_with_tutor(req: ChatRequest):
    reply = socratic_tutor_chat(user_message=req.message, mode=req.mode, grade=req.grade)
    return {"reply": reply}

# 3. Fanlar Resurslari (Darsliklar, Formulalar, DTM, Audio)
@app.get("/api/resources")
def get_resources(category: Optional[str] = None, grade: Optional[int] = None, db=Depends(get_db)):
    query = db.query(Resource)
    if category:
        query = query.filter(Resource.category == category)
    if grade:
        query = query.filter(Resource.grade == grade)
    
    results = query.all()
    if not results:
        # Standart boyitilgan resurslar
        return [
            {"id": 1, "title": "(a + b)² = a² + 2ab + b²", "category": "formula", "grade": 7, "subject": "Algebra", "content": "Yig'indining kvadrati formulasi"},
            {"id": 2, "title": "a² - b² = (a - b)(a + b)", "category": "formula", "grade": 7, "subject": "Algebra", "content": "Kvadratlar ayirmasi formulasi"},
            {"id": 3, "title": "D = b² - 4ac (Kvadrat tenglama)", "category": "formula", "grade": 8, "subject": "Algebra", "content": "Diskriminant formulasi"},
            {"id": 4, "title": "Pifagor: c² = a² + b²", "category": "formula", "grade": 8, "subject": "Geometriya", "content": "To'g'ri burchakli uchburchak gipotenuzasi"},
            {"id": 5, "title": "7-sinf Algebra (2024 Yangi nashr)", "category": "textbook", "grade": 7, "file_url": "https://edu.uz/textbooks/algebra7.pdf"},
            {"id": 6, "title": "8-sinf Geometriya (2024)", "category": "textbook", "grade": 8, "file_url": "https://edu.uz/textbooks/geom8.pdf"},
            {"id": 7, "title": "DTM-2025 Matematika 1-variant", "category": "dtm", "grade": 11, "subject": "Matematika", "content": "30 ta standart DTM savoli yechimlari bilan"},
            {"id": 8, "title": "Logarifmlar mohiyati va xossalari", "category": "audio", "grade": 10, "file_url": "https://edu.uz/audio/logarithms.mp3"}
        ]
    return results

# 4. O'yinlar: 60s Tezkor hisob savoli (Algoritmik cheksiz)
@app.get("/api/games/speed-math")
def get_speed_math_question(grade: int = 7):
    if grade <= 4:
        a = random.randint(10, 50)
        b = random.randint(5, 30)
        ans = a + b
        expr = f"{a} + {b} = ?"
    elif grade <= 8:
        a = random.randint(3, 12)
        b = random.randint(4, 9)
        c = random.randint(10, 30)
        ans = a * b - c
        expr = f"{a} × {b} - {c} = ?"
    else:
        a = random.randint(11, 25)
        ans = a * a
        expr = f"{a}² = ?"

    # Chalg'ituvchi variantlar
    distractors = [ans + random.choice([2, -2, 5, -5]), ans + random.choice([10, -10, 4])]
    options = [ans] + distractors
    random.shuffle(options)

    return {
        "expression": expr,
        "correct_answer": ans,
        "options": options
    }

# 5. Foydalanuvchi ma'lumotlarini sinxronlash (Coins, Streak, XP)
@app.post("/api/user/progress")
def update_user_progress(update: UserProgressUpdate, db=Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == update.telegram_id).first()
    if not user:
        user = User(telegram_id=update.telegram_id, name="O'quvchi", grade=7, coins=100, xp=0, streak=1)
        db.add(user)
    
    user.coins += update.coins_delta
    user.xp += update.xp_delta
    if update.increment_streak:
        user.streak += 1
    
    db.commit()
    db.refresh(user)
    return {"status": "ok", "coins": user.coins, "xp": user.xp, "streak": user.streak}

# 6. Admin: PDF Darslikni tahlil qilib bazaga yuklash
@app.post("/api/admin/parse-pdf")
async def admin_parse_pdf(file: UploadFile = File(...), grade: int = Form(7), db=Depends(get_db)):
    content = await file.read()
    problems = parse_pdf_textbook(content)
    
    saved_count = 0
    for p in problems:
        new_problem = Problem(
            question_text=p.get("question_text", ""),
            solution_steps_json=json.dumps(p.get("solution_steps", [])),
            grade=grade,
            subject="Algebra",
            topic=p.get("topic", "Darslik masalasi")
        )
        db.add(new_problem)
        saved_count += 1
    
    db.commit()
    return {"status": "success", "imported_count": saved_count, "items": problems}

# ================= STATIK FRONTEND XIZMATI =================
# Mini App va Admin UI ni to'g'ridan-to'g'ri backend orqali tarqatish
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
