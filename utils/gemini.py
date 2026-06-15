import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

async def gemini_request(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Xatolik yuz berdi: {e}"

async def masala_ber(sinf: str, fan: str, lang: str) -> str:
    til = {
        "uz": "o'zbek tilida",
        "ru": "на русском языке",
        "en": "in English"
    }.get(lang, "o'zbek tilida")
    
    prompt = f"""
Sen AI ustoz botsan. {sinf} uchun {fan} fanidan bitta masala/misol ber {til}.
Faqat masalani yoz, javobini yozma.
Masala qisqa va tushunarli bo'lsin.
"""
    return await gemini_request(prompt)

async def javob_tekshir(masala: str, foydalanuvchi_javobi: str, sinf: str, lang: str) -> str:
    til = {
        "uz": "o'zbek tilida",
        "ru": "на русском языке",
        "en": "in English"
    }.get(lang, "o'zbek tilida")
    
    prompt = f"""
Sen AI ustoz botsan. Quyidagi masalani tekshir {til}:

Masala: {masala}
O'quvchi javobi: {foydalanuvchi_javobi}
O'quvchi sinfi: {sinf}

Javob to'g'rimi yoki noto'g'rimi ayt. Agar noto'g'ri bo'lsa to'g'ri yechimni bosqichma-bosqich tushuntir.
"""
    return await gemini_request(prompt)

async def savol_javob(savol: str, sinf: str, lang: str) -> str:
    til = {
        "uz": "o'zbek tilida",
        "ru": "на русском языке",
        "en": "in English"
    }.get(lang, "o'zbek tilida")
    
    prompt = f"""
Sen AI ustoz botsan. O'quvchi savol berdi {til}.
O'quvchi sinfi: {sinf}

Savol: {savol}

Tushunarli va qisqa tushuntir. Kerak bo'lsa misol keltir.
"""
    return await gemini_request(prompt)

async def tushuntir(mavzu: str, sinf: str, lang: str) -> str:
    til = {
        "uz": "o'zbek tilida",
        "ru": "на русском языке",
        "en": "in English"
    }.get(lang, "o'zbek tilida")
    
    prompt = f"""
Sen AI ustoz botsan. Quyidagi mavzuni {sinf} o'quvchisiga {til} tushuntir:

Mavzu: {mavzu}

Batafsil va tushunarli tushuntir. Misol keltir.
"""
    return await gemini_request(prompt)

async def test_ber(sinf: str, fan: str, lang: str) -> dict:
    til = {
        "uz": "o'zbek tilida",
        "ru": "на русском языке",
        "en": "in English"
    }.get(lang, "o'zbek tilida")
    
    prompt = f"""
Sen AI ustoz botsan. {sinf} uchun {fan} fanidan bitta test savol ber {til}.
Faqat JSON formatda yoz, boshqa hech narsa yozma:
{{
    "savol": "savol matni",
    "A": "variant",
    "B": "variant", 
    "C": "variant",
    "D": "variant",
    "togri": "A"
}}
"""
    import json
    text = await gemini_request(prompt)
    try:
        text = text.strip().replace("```json", "").replace("```", "")
        return json.loads(text)
    except:
        return None

async def insho_tekshir(matn: str, mavzu: str, sinf: str, lang: str) -> str:
    til = {
        "uz": "o'zbek tilida",
        "ru": "на русском языке",
        "en": "in English"
    }.get(lang, "o'zbek tilida")
    
    prompt = f"""
Sen AI ustoz botsan. O'quvchining inshosini tekshir {til}.
O'quvchi sinfi: {sinf}
Mavzu: {mavzu}

Insho:
{matn}

Baho ber (1-10), kuchli va zaif tomonlarini ayt, tavsiyalar ber.
"""
    return await gemini_request(prompt)
