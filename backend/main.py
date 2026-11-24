from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import random
import json

from database import SessionLocal, init_db, User, Resource, Problem, Duel
from services.ai_service import solve_math_problem, socratic_tutor_chat
from services.parser_service import parse_pdf_textbook

app = FastAPI(title="Mathy API", version="1.0.0", description="Mathy EdTech AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup
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

# ================= ROUTES =================

@app.get("/")
def root():
    return {"status": "ok", "service": "Mathy API - EdTech Platform"}

# 1. Foto / Matn orqali masalani tahlil qilish (Doska rejimi)
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

# 3. Fanlar Resurslari (Darsliklar, Formulalar, DTM)
@app.get("/api/resources")
def get_resources(category: Optional[str] = None, grade: Optional[int] = None, db=Depends(get_db)):
    query = db.query(Resource)
    if category:
        query = query.filter(Resource.category == category)
    if grade:
        query = query.filter(Resource.grade == grade)
    
    results = query.all()
    if not results:
        # Default mock resurslar
        return [
            {"id": 1, "title": "(a + b)² = a² + 2ab + b²", "category": "formula", "grade": 7, "subject": "Algebra"},
            {"id": 2, "title": "7-sinf Algebra (2024)", "category": "textbook", "grade": 7, "file_url": "https://example.com/algebra7.pdf"},
            {"id": 3, "title": "DTM-2025 Matematika 1-variant", "category": "dtm", "grade": 11, "subject": "Matematika"},
            {"id": 4, "title": "Logarifmlar mohiyati", "category": "audio", "grade": 10, "file_url": "https://example.com/audio1.mp3"}
        ]
    return results

# 4. O'yinlar: 60s Tezkor hisob savoli (Cheksiz generatsiya)
@app.get("/api/games/speed-math")
def get_speed_math_question(grade: int = 7):
    # Har safar yangi original misol
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

    # Variantlar
    options = [ans, ans + random.choice([2, -2, 5, -5]), ans + random.choice([10, -10, 4])]
    random.shuffle(options)

    return {
        "expression": expr,
        "correct_answer": ans,
        "options": options
    }

# 5. Admin: PDF Darslikni tahlil qilib bazaga yuklash
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
