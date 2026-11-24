"""
Mathy EdTech Platformasi uchun ma'lumotlar bazasini boyitish skripti (Database Seeder).
Ushbu skript O'zbekiston maktab ta'limi standarti bo'yicha formulalar, darsliklar va testlarni kiritadi.
"""

from database import SessionLocal, init_db, Resource, Problem, User
import json

def seed():
    init_db()
    db = SessionLocal()

    # Agar ma'lumotlar mavjud bo'lsa, qayta yuklamaymiz
    if db.query(Resource).count() > 0:
        print("ℹ️ Ma'lumotlar bazasida resurslar allaqachon mavjud.")
        db.close()
        return

    print("🌱 Baza boshlang'ich ta'lim resurslari bilan to'ldirilmoqda...")

    resources = [
        # Formulalar
        Resource(
            title="(a + b)² = a² + 2ab + b²",
            category="formula",
            grade=7,
            subject="Algebra",
            content="Yig'indining kvadrati: Ikki son yig'indisining kvadrati birinchi son kvadrati, ular ko'paytmasining ikkilangani va ikkinchi son kvadratining yig'indisiga teng."
        ),
        Resource(
            title="(a - b)² = a² - 2ab + b²",
            category="formula",
            grade=7,
            subject="Algebra",
            content="Ayirmaning kvadrati: Birinchi son kvadrati minus ikkilangan ko'paytma plyus ikkinchi son kvadrati."
        ),
        Resource(
            title="a² - b² = (a - b)(a + b)",
            category="formula",
            grade=7,
            subject="Algebra",
            content="Kvadratlar ayirmasi formulasi: Ko'paytuvchilarga ajratishda eng ko'p ishlatiladigan asosiy qoida."
        ),
        Resource(
            title="D = b² - 4ac",
            category="formula",
            grade=8,
            subject="Algebra",
            content="Kvadrat tenglama diskriminanti. Agar D > 0 bo'lsa 2 ta ildiz, D = 0 bo'lsa 1 ta ildiz, D < 0 bo'lsa haqiqiy ildizga ega emas."
        ),
        Resource(
            title="Pifagor: a² + b² = c²",
            category="formula",
            grade=8,
            subject="Geometriya",
            content="To'g'ri burchakli uchburchak katetlari kvadratlarining yig'indisi gipotenuza kvadratiga teng."
        ),
        Resource(
            title="sin²α + cos²α = 1",
            category="formula",
            grade=9,
            subject="Geometriya / Trigonometriya",
            content="Trigonometriyaning asosiy ayniyati."
        ),

        # Darsliklar (PDF)
        Resource(
            title="7-sinf Algebra (2024 Yangi darslik)",
            category="textbook",
            grade=7,
            subject="Algebra",
            file_url="https://kitob.uz/textbooks/algebra7_2024.pdf"
        ),
        Resource(
            title="8-sinf Geometriya (2024 Yangi darslik)",
            category="textbook",
            grade=8,
            subject="Geometriya",
            file_url="https://kitob.uz/textbooks/geometriya8_2024.pdf"
        ),
        Resource(
            title="9-sinf Algebra (O'quv qo'llanma)",
            category="textbook",
            grade=9,
            subject="Algebra",
            file_url="https://kitob.uz/textbooks/algebra9.pdf"
        ),
        Resource(
            title="10-11 sinflar Matematika kursi",
            category="textbook",
            grade=11,
            subject="Matematika",
            file_url="https://kitob.uz/textbooks/matematika10_11.pdf"
        ),

        # DTM & Milliy Sertifikat
        Resource(
            title="DTM-2025 Matematika Asosiy Blok (1-variant)",
            category="dtm",
            grade=11,
            subject="Matematika",
            content="30 ta test savollari, qiyinlik darajalari va to'liq yechimlari bilan."
        ),
        Resource(
            title="Milliy Sertifikat: A+ Darajali Masalalar To'plami",
            category="dtm",
            grade=11,
            subject="Matematika",
            content="Oliy toifali o'quvchilar va sertifikatga tayyorlanuvchilar uchun murakkab nostandart masalalar."
        ),

        # Audio Konspektlar
        Resource(
            title="Logarifmlar mohiyati va asosiy xossalari",
            category="audio",
            grade=10,
            subject="Algebra",
            file_url="https://audio.mathy.uz/logarithms_intro.mp3",
            content="4 daqiqalik dars: Nega logarifm o'ylab topilgan va amalda qayerda ishlatiladi?"
        ),
        Resource(
            title="Hosila tushunchasi (Tezlik va o'zgarish)",
            category="audio",
            grade=11,
            subject="Algebra",
            file_url="https://audio.mathy.uz/derivatives_concept.mp3",
            content="5 daqiqalik dars: Fizika va geometriyada hosilaning amaliy ma'nosi."
        )
    ]

    for res in resources:
        db.add(res)

    # Boshlang'ich test foydalanuvchisi
    test_user = User(
        telegram_id=99988877,
        name="Azizbek",
        grade=7,
        coins=520,
        streak=5,
        xp=240
    )
    db.add(test_user)

    db.commit()
    print("✅ Ma'lumotlar bazasi muvaffaqiyatli to'ldirildi!")
    db.close()

if __name__ == "__main__":
    seed()
