import json
from config import GEMINI_API_KEY

try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
except Exception:
    client = None

def solve_math_problem(image_bytes: bytes = None, text_prompt: str = None, grade: int = 7) -> dict:
    """
    Multimodal Gemini orqali masalani tahlil qiladi va qadamma-qadam yechim + audio matn qaytaradi.
    """
    system_instruction = f"""
    Siz 5-11 sinf o'quvchilari uchun o'zbek tilidagi eng do'stona, sabrli matematika repetitorisiz.
    O'quvchi {grade}-sinfda o'qiydi.
    Masalani tahlil qiling va quyidagi JSON formatida javob bering:
    {{
      "title": "Masalaning qisqa nomi yoki formulasi",
      "topic": "Algebra / Geometriya mavzusi",
      "steps": [
        {{
          "step_num": 1,
          "title": "1-qadam sarlavhasi (masalan, Qavslarni ochish)",
          "detail": "Batafsil hisoblash formulasi va harakati"
        }}
      ],
      "final_answer": "Javob: x = 5",
      "audio_script": "O'quvchiga xuddi repetitor audio xabar yuborayotgandek iliq, sodda o'zbek tilidagi tushuntirish matni (40-60 so'z)"
    }}
    Faqat toza JSON qaytaring.
    """

    if client:
        try:
            contents = []
            if image_bytes:
                contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
            if text_prompt:
                contents.append(text_prompt)
            else:
                contents.append("Masalani yechib bering.")

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print("Gemini API xatosi:", e)

    # Fallback / Prototip namunasi
    return {
        "title": text_prompt or "2(3x - 4) + 6 = 20",
        "topic": "Chiziqli tenglamalar",
        "steps": [
            {
                "step_num": 1,
                "title": "Qavslarni ochish va soddalashtirish",
                "detail": "2 ni qavs ichiga ko'paytiramiz: 6x - 8 + 6 = 20 ➔ 6x - 2 = 20"
            },
            {
                "step_num": 2,
                "title": "Noma'lumni ajratish va javob",
                "detail": "6x = 20 + 2 = 22 ➔ x = 22 / 6 = 3⅔"
            }
        ],
        "final_answer": "x = 3⅔",
        "audio_script": f"Salom! Qara, bu yerda qavsli tenglama turibdi. Birinchi bo'lib qavsni ochdik, so'ng ozod hadlarni o'ng tomonga o'tkazdik. Natijada x teng 3 butun 3 dan 2 chiqdi!"
    }

def socratic_tutor_chat(user_message: str, history: list = None, mode: str = "socratic", grade: int = 7) -> str:
    """
    Sokratik rejimda o'quvchiga darhol tayyor javobni aytmasdan, savollar bilan o'zi yechishga undaydi.
    """
    prompt = f"""
    Siz O'zbekistondagi {grade}-sinf o'quvchisi uchun shaxsiy AI matematika repetitorisiz.
    Rejim: {'Sokratik (javobni to\'g\'ridan-to\'g\'ri aytma, o\'quvchini savollar berib to\'g\'ri yo\'naltir)' if mode == 'socratic' else 'To\'g\'ridan-to\'g\'ri yechim va tushuntirish'}.
    O'quvchining so'rovi: "{user_message}".
    Javobingiz qisqa (2-4 gap), samimiy va emojilar bilan rag'batlantiruvchi bo'lsin.
    """

    if client:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print("Gemini Chat xatosi:", e)

    return "Ajoyib savol! 💡 Buni tushunish uchun avval eslaylik: tenglamaning ikkala tomoniga bir xil amal bajarsak tenglik o'zgaradimi? Nima deb o'ylaysan?"
