# 🚀 Mathy — AI Foto-Tyutor & Ta'lim Platformasi (Telegram Mini App)

> **"Shunchaki yechim emas — tushunish kafolati."**

**Mathy** — bu maktab o'quvchilari (1–11 sinflar) va abituriyentlar uchun sun'iy intellektga asoslangan shaxsiy repetitor va interaktiv ta'lim ekotizimi. Loyiha Telegram Mini App formatida ishlab chiqilgan bo'lib, o'rnatishni talab qilmaydi va virusli do'stlar duelini qo'llab-quvvatlaydi.

---

## 🌟 Asosiy Imkoniyatlar

1. 📸 **Foto-Tyutor (Doska rejimi):**
   - Daftardagi yoki darslikdagi masalani rasmga oladi (qo'lyozma, formulalar va geometrik chizmalar).
   - Ekran interaktiv qora doskaga aylanadi: bosqichma-bosqich qadamlar tushuntiriladi.
   - O'zbek tilida tabiiy ovozli tushuntirish va jonli audio to'lqinlar (equalizer).
   - Har bir qadam ochilib-yopiladigan akkordeon shaklida.

2. 🧠 **AI Tyutor Lab (Sokratik Suhbat):**
   - Ikki xil rejim: *Sokratik (yo'naltiruvchi)* va *To'g'ridan-to'g'ri yechim*.
   - Ovozli va matnli savol-javob ("Nega bu yerda 2 ga ko'paytirdik?").

3. 📚 **Fanlar Resurslari & Kutubxona:**
   - 1–11 sinf matematika, algebra va geometriya darsliklari (PDF).
   - Barcha muhim formulalar spravochnigi (qidiruv va toifalar bilan).
   - DTM va Milliy sertifikat test namunalari va yechimlari.
   - Tezkor qoidalar, layfxaklar va audio-konspektlar.

4. 🎮 **O'yinlar va Duellar:**
   - 1v1 Telegram do'stlar jangi (havola orqali chaqirish).
   - 60 soniyali "Tezkor hisob" mini-o'yini.
   - Reytinglar (Maktablar va Viloyatlar kesimida).
   - Duolingo uslubidagi kunlik olov (Streak) va MathCoin yutuqlari.

5. ⚡ **Smart Baza & AI PDF Parser (Admin):**
   - Darslik yoki test kitoblarining PDF shaklini yuklash orqali avtomatik minglab masalalarni bazaga raqamlashtirish.
   - Cheksiz yangi misollarni real vaqtda generatsiya qilish algoritmi.

---

## 🛠 Texnologiyalar Steki

- **Frontend:** Telegram WebApp SDK, HTML5, Tailwind CSS, Modern Vanilla JS (No build-step needed, ultra-yengil va tez ochiladi).
- **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic.
- **Telegram Bot:** Aiogram 3.x (WebAppData, Inline duellar).
- **AI Core:** Google Gemini 2.5/Flash Multimodal Vision & Reasoning API.
- **Database:** SQLite / PostgreSQL (SQLAlchemy ORM).

---

## 📂 Loyiha Tuzilishi

```
mathy-app/
├── frontend/
│   ├── index.html        # Telegram Mini App asosiy interfeysi (Doska, AI Lab, Kutubxona, O'yinlar)
│   ├── css/style.css     # Maxsus animatsiyalar, neon effektlar, qora doska
│   └── js/app.js         # Telegram SDK integratsiyasi, Audio, Chat, O'yin mantiqi
├── backend/
│   ├── main.py           # FastAPI REST API server
│   ├── bot.py            # Aiogram Telegram Bot
│   ├── config.py         # Konfiguratsiya va API kalitlar
│   ├── database.py       # Ma'lumotlar bazasi modellari
│   ├── services/
│   │   ├── ai_service.py     # Gemini Vision & Audio tushuntirish servisi
│   │   └── parser_service.py # PDF darsliklarni avtomatik bazaga o'giruvchi parser
│   └── requirements.txt  # Python kutubxonalari
├── README.md
└── .gitignore
```

---

## 🚀 Ishga Tushirish

### 1. Backend & Bot:
```bash
cd backend
python -m venv venv
# Windows uchun:
venv\Scripts\activate
# Linux/Mac uchun:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env # Telegram Bot Token va Gemini API kalitini kiriting

# FastAPI serverini yoqish:
uvicorn main:app --reload --port 8000

# Telegram Botni yoqish:
python bot.py
```

### 2. Frontend (Mini App):
Frontend statik fayllardan iborat bo'lib, istalgan server yoki Vercel / Netlify / Cloudflare Pages orqali bir bosishda joylanishi mumkin.

---

## 👨‍💻 Muallif
**Quvondiq Abdurasulov** ([@abdurasulovuz](https://github.com/abdurasulovuz))
