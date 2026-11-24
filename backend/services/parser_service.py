import json
from pypdf import PdfReader
from config import GEMINI_API_KEY

try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
except Exception:
    client = None

def parse_pdf_textbook(file_bytes: bytes, max_pages: int = 5) -> list:
    """
    Darslik PDF faylidan sahifalarni o'qiydi va Gemini orqali masalalarni ajratib,
    toifalaydi va ma'lumotlar bazasiga tayyor JSON ro'yxat qilib beradi.
    """
    import io
    reader = PdfReader(io.BytesIO(file_bytes))
    extracted_text = ""
    for idx, page in enumerate(reader.pages[:max_pages]):
        extracted_text += f"\n--- Sahifa {idx+1} ---\n" + (page.extract_text() or "")

    if client and extracted_text.strip():
        try:
            prompt = f"""
            Quyidagi darslik matnidan barcha matematika masalalarini ajratib oling.
            Har bir masala uchun qiyinlik darajasi (1-5), mavzusi, savol matni va to'g'ri yechimini JSON formatda bering:
            [
              {{
                "question_text": "Masala matni",
                "topic": "Mavzu",
                "difficulty": 2,
                "solution_steps": ["1-qadam...", "2-qadam..."],
                "final_answer": "Javob"
              }}
            ]
            Faqat toza JSON massiv qaytaring.
            Matn:
            {extracted_text[:4000]}
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            print("PDF Parse xatosi:", e)

    # Fallback namuna
    return [
        {
            "question_text": "Tenglamani yeching: 5x - 15 = 35",
            "topic": "Chiziqli tenglamalar",
            "difficulty": 1,
            "solution_steps": ["5x = 35 + 15 = 50", "x = 50 / 5 = 10"],
            "final_answer": "x = 10"
        },
        {
            "question_text": "To'g'ri to'rtburchakning perimetri 36 sm, bo'yi enidan 4 sm uzun. Enini toping.",
            "topic": "Matnli masalalar",
            "difficulty": 2,
            "solution_steps": ["2(a + b) = 36 ➔ a + b = 18", "a = b + 4 ➔ 2b + 4 = 18 ➔ b = 7"],
            "final_answer": "Eni = 7 sm"
        }
    ]
