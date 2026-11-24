import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://math-app-4tum.vercel.app")

# Vercel serverless muhitida faqat /tmp papkasi yozish uchun ochiq
if os.getenv("VERCEL"):
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/mathy.db")
    UPLOAD_DIR = "/tmp/uploads"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mathy.db")
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "mathy2026")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "mathy-super-secret-key-change-me-in-production")
