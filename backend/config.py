import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mathy.db")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-mini-app-domain.com")

# Admin Panel xavfsizlik sozlamalari
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "mathy2026")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "mathy-super-secret-key-change-me-in-production")

# Fayllar saqlanadigan papka
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
