import aiohttp
from config import GEMINI_API_KEY

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

async def gemini_request(prompt: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            async with session.post(API_URL, json=payload) as resp:
                data = await resp.json()
                if "candidates" in data:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    return f"API xatosi: {data}"
    except Exception as e:
        return f"Xatolik: {e}"

async def masala_ber(sinf: str, fan: str, lang: str) -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    prompt = f"Sen AI ustoz botsan. {sinf} uchun {fan} fanidan bitta masala/misol ber {til}. Faqat masalani yoz, javobini yozma. Masala qisqa va tushunarli bo'lsin."
    return await gemini_request(prompt)

async def javob_tekshir(masala: str, foydalanuvchi_javobi: str, sinf: str, lang: str) -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    prompt = f"Sen AI ustoz botsan. Quyidagi masalani tekshir {til}:\nMasala: {masala}\nO'quvchi javobi: {foydalanuvchi_javobi}\nO'quvchi sinfi: {sinf}\nJavob to'g'rimi yoki noto'g'rimi ayt. Agar noto'g'ri bo'lsa to'g'ri yechimni bosqichma-bosqich tushuntir."
    return await gemini_request(prompt)

async def savol_javob(savol: str, sinf: str, lang: str) -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    prompt = f"Sen AI ustoz botsan. O'quvchi savol berdi {til}.\nO'quvchi sinfi: {sinf}\nSavol: {savol}\nTushunarli va qisqa tushuntir. Kerak bo'lsa misol keltir."
    return await gemini_request(prompt)

async def tushuntir(mavzu: str, sinf: str, lang: str) -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    prompt = f"Sen AI ustoz botsan. Quyidagi mavzuni {sinf} o'quvchisiga {til} tushuntir:\nMavzu: {mavzu}\nBatafsil va tushunarli tushuntir. Misol keltir."
    return await gemini_request(prompt)

async def test_ber(sinf: str, fan: str, lang: str) -> dict:
    import json
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    prompt = f"""Sen AI ustoz botsan. {sinf} uchun {fan} fanidan bitta test savol ber {til}.
Faqat JSON formatda yoz, boshqa hech narsa yozma:
{{"savol": "savol matni", "A": "variant", "B": "variant", "C": "variant", "D": "variant", "togri": "A"}}"""
    text = await gemini_request(prompt)
    try:
        text = text.strip().replace("```json", "").replace("```", "")
        return json.loads(text)
    except:
        return None

async def insho_tekshir(matn: str, mavzu: str, sinf: str, lang: str) -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    prompt = f"Sen AI ustoz botsan. O'quvchining inshosini tekshir {til}.\nO'quvchi sinfi: {sinf}\nMavzu: {mavzu}\nInsho:\n{matn}\nBaho ber (1-10), kuchli va zaif tomonlarini ayt, tavsiyalar ber."
    return await gemini_request(prompt)
