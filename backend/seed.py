"""
Mathy bazani boshlang'ich ta'lim resurslari bilan boyitish (seed) skripti.
"""
from database import SessionLocal, init_db, Resource, Problem, User
import json

def seed():
    init_db()
    db = SessionLocal()

    if db.query(Resource).count() > 0:
        print("ℹ️ Ma'lumotlar bazasida resurslar allaqachon mavjud. O'tkazib yuborildi.")
        db.close()
        return

    print("🌱 Baza boshlang'ich resurslar bilan to'ldirilmoqda...")

    resources = [
        Resource(title="(a + b)² = a² + 2ab + b²", category="formula", grade=7, subject="Algebra",
                 content="Yig'indining kvadrati formulasi"),
        Resource(title="(a - b)² = a² - 2ab + b²", category="formula", grade=7, subject="Algebra",
                 content="Ayirmaning kvadrati formulasi"),
        Resource(title="a² - b² = (a - b)(a + b)", category="formula", grade=7, subject="Algebra",
                 content="Kvadratlar ayirmasi formulasi"),
        Resource(title="D = b² - 4ac", category="formula", grade=8, subject="Algebra",
                 content="Kvadrat tenglama diskriminanti"),
        Resource(title="Pifagor: a² + b² = c²", category="formula", grade=8, subject="Geometriya",
                 content="To'g'ri burchakli uchburchak uchun"),
        Resource(title="sin²α + cos²α = 1", category="formula", grade=9, subject="Geometriya",
                 content="Trigonometriyaning asosiy ayniyati"),
        Resource(title="7-sinf Algebra (2024)", category="textbook", grade=7, subject="Algebra"),
        Resource(title="8-sinf Geometriya (2024)", category="textbook", grade=8, subject="Geometriya"),
        Resource(title="DTM-2025 Matematika 1-variant", category="dtm", grade=11, subject="Matematika",
                 content="30 ta test savoli yechimlari bilan"),
        Resource(title="Logarifmlar mohiyati", category="audio", grade=10, subject="Algebra",
                 content="4 daqiqalik audio tushuntirish"),
    ]

    problems = [
        Problem(question_text="5x - 15 = 35", solution_steps_json=json.dumps(["5x = 50", "x = 10"]),
                grade=7, subject="Algebra", topic="Chiziqli tenglamalar", difficulty=1, source="seed"),
        Problem(question_text="To'g'ri to'rtburchak perimetri 36 sm, bo'yi enidan 4 sm uzun. Enini toping.",
                solution_steps_json=json.dumps(["2(a+b)=36", "a+b=18", "a=b+4", "2b+4=18", "b=7"]),
                grade=7, subject="Algebra", topic="Matnli masalalar", difficulty=2, source="seed"),
    ]

    for r in resources:
        db.add(r)
    for p in problems:
        db.add(p)

    db.commit()
    print("✅ Bazaga 10 ta resurs va 2 ta namuna masala joylandi.")
    db.close()

if __name__ == "__main__":
    seed()
