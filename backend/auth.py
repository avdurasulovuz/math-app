"""
Mathy Admin Panel uchun autentifikatsiya (JWT token asosida).
"""
import hashlib
import hmac
import json
import time
import base64
from config import ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_SECRET_KEY


def verify_admin(username: str, password: str) -> bool:
    """Login va parolni tekshiradi."""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def create_token(username: str) -> str:
    """Oddiy JWT-ga o'xshash vaqtli token yaratadi (24 soatga amal qiladi)."""
    payload = {
        "sub": username,
        "exp": int(time.time()) + 86400,  # 24 soat
        "iat": int(time.time())
    }
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    signature = hmac.new(ADMIN_SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def verify_token(token: str) -> bool:
    """Tokenni tekshiradi: imzo to'g'rimi va muddati o'tmaganmi."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return False
        payload_b64, signature = parts
        expected_sig = hmac.new(ADMIN_SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return False
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        if payload.get("exp", 0) < time.time():
            return False
        return True
    except Exception:
        return False
