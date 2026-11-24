from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import random
import json
import os
import shutil

from database import SessionLocal, init_db, User, Resource, Problem, Duel
from services.ai_service import solve_math_problem, socratic_tutor_chat
from services.parser_service import parse_pdf_textbook
from auth import verify_admin, create_token, verify_token
from config import UPLOAD_DIR

app = FastAPI(title="Mathy API", version="1.0.0", description="Mathy EdTech AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    try:
        init_db()
    except Exception as e:
        print("DB init note:", e)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin(authorization: str = Header(None)):
    """Admin tokenini tekshirish. Har bir himoyalangan route uchun ishlatiladi."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token topilmadi")
    token = authorization.replace("Bearer ", "")
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati o'tgan")
    return True


# ===================== PYDANTIC SCHEMAS =====================

class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    message: str
    mode: Optional[str] = "socratic"
    grade: Optional[int] = 7

class ResourceCreate(BaseModel):
    title: str
    category: str
    grade: int = 7
    subject: str = "Algebra"
    content: Optional[str] = None

class ProblemCreate(BaseModel):
    question_text: str
    solution_steps: List[str]
    grade: int = 7
    subject: str = "Algebra"
    topic: str = "Tenglamalar"
    difficulty: int = 1

class UserProgressUpdate(BaseModel):
    telegram_id: int
    coins_delta: int = 0
    xp_delta: int = 0
    increment_streak: bool = False


# ===================== ADMIN AUTH =====================

@app.post("/api/admin/login")
def admin_login(req: LoginRequest):
    """Admin login — to'g'ri login va parol bilan token olish."""
    if not verify_admin(req.username, req.password):
        raise HTTPException(status_code=401, detail="Login yoki parol noto'g'ri")
    token = create_token(req.username)
    return {"status": "ok", "token": token, "message": "Muvaffaqiyatli kirildi!"}


@app.get("/api/admin/verify")
def admin_verify(auth: bool = Depends(require_admin)):
    """Token haqiqiyligi va amal qilish muddatini tekshirish."""
    return {"status": "ok", "valid": True}


# ===================== ADMIN: STATISTIKA =====================

@app.get("/api/admin/stats")
def admin_stats(auth: bool = Depends(require_admin), db=Depends(get_db)):
    """Admin dashboard uchun bosh statistika."""
    total_problems = db.query(Problem).count()
    active_problems = db.query(Problem).filter(Problem.is_active == True).count()
    total_resources = db.query(Resource).count()
    total_users = db.query(User).count()
    total_duels = db.query(Duel).count()
    return {
        "total_problems": total_problems,
        "active_problems": active_problems,
        "total_resources": total_resources,
        "total_users": total_users,
        "total_duels": total_duels
    }


# ===================== ADMIN: MASALALAR BOSHQARUVI =====================

@app.get("/api/admin/problems")
def admin_list_problems(
    grade: Optional[int] = None,
    subject: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    auth: bool = Depends(require_admin),
    db=Depends(get_db)
):
    """Bazadagi masalalar ro'yxati (sahifalash bilan)."""
    query = db.query(Problem)
    if grade:
        query = query.filter(Problem.grade == grade)
    if subject:
        query = query.filter(Problem.subject == subject)
    total = query.count()
    items = query.order_by(Problem.id.desc()).offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "items": [
            {
                "id": p.id,
                "question_text": p.question_text,
                "grade": p.grade,
                "subject": p.subject,
                "topic": p.topic,
                "difficulty": p.difficulty,
                "source": p.source,
                "is_active": p.is_active,
                "created_at": str(p.created_at)
            }
            for p in items
        ]
    }


@app.post("/api/admin/problems")
def admin_add_problem(req: ProblemCreate, auth: bool = Depends(require_admin), db=Depends(get_db)):
    """Yangi masala qo'lda qo'shish."""
    new = Problem(
        question_text=req.question_text,
        solution_steps_json=json.dumps(req.solution_steps),
        grade=req.grade,
        subject=req.subject,
        topic=req.topic,
        difficulty=req.difficulty,
        source="manual"
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return {"status": "ok", "id": new.id}


@app.delete("/api/admin/problems/{problem_id}")
def admin_delete_problem(problem_id: int, auth: bool = Depends(require_admin), db=Depends(get_db)):
    """Masalani o'chirish (yoki yashirish)."""
    p = db.query(Problem).filter(Problem.id == problem_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Masala topilmadi")
    p.is_active = False
    db.commit()
    return {"status": "ok", "message": f"Masala #{problem_id} o'chirildi"}


# ===================== ADMIN: TESTLAR VA PDF IMPORT =====================

@app.post("/api/admin/upload-tests")
async def admin_upload_tests(
    file: UploadFile = File(...),
    grade: int = Form(7),
    subject: str = Form("Algebra"),
    auth: bool = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Admin PDF yoki rasmli test faylini yuklaydi.
    AI tahlil qiladi va masalalarni bazaga saqlaydi.
    """
    # Faylni diskka saqlash
    safe_name = f"{grade}_{subject}_{file.filename}".replace(" ", "_")
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # AI orqali tahlil qilish
    problems = parse_pdf_textbook(content, max_pages=50)

    saved_count = 0
    for p in problems:
        new_problem = Problem(
            question_text=p.get("question_text", ""),
            solution_steps_json=json.dumps(p.get("solution_steps", [])),
            grade=grade,
            subject=subject,
            topic=p.get("topic", "Darslik masalasi"),
            difficulty=p.get("difficulty", 1),
            source="pdf_import"
        )
        db.add(new_problem)
        saved_count += 1

    db.commit()
    return {
        "status": "success",
        "file_saved": safe_name,
        "imported_count": saved_count,
        "items": problems
    }


# ===================== ADMIN: RESURSLAR BOSHQARUVI =====================

@app.get("/api/admin/resources")
def admin_list_resources(
    category: Optional[str] = None,
    auth: bool = Depends(require_admin),
    db=Depends(get_db)
):
    """Barcha resurslar ro'yxati."""
    query = db.query(Resource)
    if category:
        query = query.filter(Resource.category == category)
    items = query.order_by(Resource.id.desc()).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "category": r.category,
            "grade": r.grade,
            "subject": r.subject,
            "file_name": r.file_name,
            "content": r.content,
            "is_active": r.is_active,
            "created_at": str(r.created_at)
        }
        for r in items
    ]


@app.post("/api/admin/resources")
async def admin_add_resource(
    title: str = Form(...),
    category: str = Form(...),
    grade: int = Form(7),
    subject: str = Form("Algebra"),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    auth: bool = Depends(require_admin),
    db=Depends(get_db)
):
    """Yangi resurs qo'shish (fayl bilan yoki faylsiz)."""
    file_url = None
    file_name = None

    if file:
        safe_name = f"res_{category}_{grade}_{file.filename}".replace(" ", "_")
        file_path = os.path.join(UPLOAD_DIR, safe_name)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        file_url = f"/api/files/{safe_name}"
        file_name = file.filename

    new = Resource(
        title=title,
        category=category,
        grade=grade,
        subject=subject,
        file_url=file_url,
        file_name=file_name,
        content=content
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return {"status": "ok", "id": new.id}


@app.delete("/api/admin/resources/{resource_id}")
def admin_delete_resource(resource_id: int, auth: bool = Depends(require_admin), db=Depends(get_db)):
    """Resursni o'chirish."""
    r = db.query(Resource).filter(Resource.id == resource_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Resurs topilmadi")
    r.is_active = False
    db.commit()
    return {"status": "ok"}


# ===================== ADMIN: FOYDALANUVCHILAR =====================

@app.get("/api/admin/users")
def admin_list_users(
    page: int = 1,
    limit: int = 50,
    auth: bool = Depends(require_admin),
    db=Depends(get_db)
):
    """O'quvchilar ro'yxati (Telegram ID, ism, sinf, coins, streak)."""
    total = db.query(User).count()
    items = db.query(User).order_by(User.id.desc()).offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "items": [
            {
                "id": u.id,
                "telegram_id": u.telegram_id,
                "name": u.name,
                "grade": u.grade,
                "coins": u.coins,
                "streak": u.streak,
                "xp": u.xp,
                "level": u.level,
                "created_at": str(u.created_at)
            }
            for u in items
        ]
    }


# ===================== YUKLANGAN FAYLLARNI TARQATISH =====================

@app.get("/api/files/{filename}")
def serve_file(filename: str):
    """Yuklangan fayllarni yuklab olish uchun."""
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Fayl topilmadi")
    return FileResponse(path, filename=filename)


# ===================== OMMAVIY ENDPOINTLAR (Mini App uchun) =====================

@app.get("/")
def root():
    return {"status": "ok", "service": "Mathy API v1.0"}


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


@app.post("/api/chat")
def chat_with_tutor(req: ChatRequest):
    reply = socratic_tutor_chat(user_message=req.message, mode=req.mode, grade=req.grade)
    return {"reply": reply}


@app.get("/api/resources")
def get_resources(category: Optional[str] = None, grade: Optional[int] = None, db=Depends(get_db)):
    query = db.query(Resource).filter(Resource.is_active == True)
    if category:
        query = query.filter(Resource.category == category)
    if grade:
        query = query.filter(Resource.grade == grade)
    items = query.all()
    return [
        {
            "id": r.id, "title": r.title, "category": r.category,
            "grade": r.grade, "subject": r.subject,
            "file_url": r.file_url, "content": r.content
        }
        for r in items
    ]


@app.get("/api/games/speed-math")
def get_speed_math_question(grade: int = 7):
    if grade <= 4:
        a, b = random.randint(10, 50), random.randint(5, 30)
        ans = a + b
        expr = f"{a} + {b} = ?"
    elif grade <= 8:
        a, b, c = random.randint(3, 12), random.randint(4, 9), random.randint(10, 30)
        ans = a * b - c
        expr = f"{a} × {b} - {c} = ?"
    else:
        a = random.randint(11, 25)
        ans = a * a
        expr = f"{a}² = ?"
    options = list({ans, ans + random.choice([2, -2, 5]), ans + random.choice([10, -10, 4])})
    while len(options) < 3:
        options.append(ans + random.randint(-8, 8))
    random.shuffle(options)
    return {"expression": expr, "correct_answer": ans, "options": options}


@app.post("/api/user/progress")
def update_user_progress(update: UserProgressUpdate, db=Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == update.telegram_id).first()
    if not user:
        user = User(telegram_id=update.telegram_id)
        db.add(user)
    user.coins += update.coins_delta
    user.xp += update.xp_delta
    if update.increment_streak:
        user.streak += 1
    db.commit()
    db.refresh(user)
    return {"coins": user.coins, "xp": user.xp, "streak": user.streak}


# ===================== STATIC FILES =====================

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
