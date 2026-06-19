import aiohttp
from config import GROQ_API_KEY

API_URL = "https://api.groq.com/openai/v1/chat/completions"

async def groq_request(prompt: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=headers, json=payload) as resp:
                data = await resp.json()
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"API xatosi: {data}"
    except Exception as e:
        return f"Xatolik: {e}"

async def masala_ber(sinf: str, fan: str, lang: str, ism: str = "") -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    ism_korsatma = f"O'quvchining ismi {ism}. Masalani '{ism}' deb murojaat qilib boshla." if ism else ""
    prompt = f"""Sen AI ustoz botsan. {ism_korsatma}
{sinf} uchun {fan} fanidan bitta masala/misol ber {til}. Faqat masalani yoz, javobini yozma. Masala qisqa va tushunarli bo'lsin."""
    return await groq_request(prompt)

async def javob_tekshir(masala: str, foydalanuvchi_javobi: str, sinf: str, lang: str, ism: str = "") -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    ism_korsatma = f"O'quvchining ismi {ism}. Javobni '{ism}' deb murojaat qilib boshla." if ism else ""
    prompt = f"""Sen AI ustoz botsan. {ism_korsatma}
Quyidagi masalani tekshir {til}:
Masala: {masala}
O'quvchi javobi: {foydalanuvchi_javobi}
O'quvchi sinfi: {sinf}
Javob to'g'rimi yoki noto'g'rimi ayt. Agar noto'g'ri bo'lsa to'g'ri yechimni bosqichma-bosqich tushuntir."""
    return await groq_request(prompt)

async def savol_javob(savol: str, sinf: str, lang: str, ism: str = "", uzun: bool = False) -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    
    if uzun:
        uzunlik_korsatma = "BATAFSIL javob ber: kamida 150-200 so'z, misollar bilan, bosqichma-bosqich tushuntir."
    else:
        uzunlik_korsatma = "QISQA javob ber: maksimum 2-3 jumla, faqat asosiy javob, ortiqcha tushuntirishsiz."
    
    ism_korsatma = f"O'quvchining ismi {ism}. Javobni '{ism}' deb murojaat qilib boshla." if ism else ""
    
    prompt = f"""Sen AI ustoz botsan. {ism_korsatma}
O'quvchi sinfi: {sinf}
Savol: {savol}

MUHIM QOIDA: {uzunlik_korsatma}

Javobni {til} yoz."""
    return await groq_request(prompt)

async def tushuntir(mavzu: str, sinf: str, lang: str, ism: str = "", uzun: bool = False) -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    
    if uzun:
        uzunlik_korsatma = "BATAFSIL tushuntir: kamida 150-200 so'z, misollar bilan, bosqichma-bosqich."
    else:
        uzunlik_korsatma = "QISQA tushuntir: maksimum 2-3 jumla, faqat eng muhim narsani ayt."
    
    ism_korsatma = f"O'quvchining ismi {ism}. Tushuntirishni '{ism}' deb murojaat qilib boshla." if ism else ""
    
    prompt = f"""Sen AI ustoz botsan. {ism_korsatma}
O'quvchi sinfi: {sinf}
Mavzu: {mavzu}

MUHIM QOIDA: {uzunlik_korsatma}

Tushuntirishni {til} yoz."""
    return await groq_request(prompt)

async def test_ber(sinf: str, fan: str, lang: str) -> dict:
    import json
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    prompt = f"""Sen AI ustoz botsan. {sinf} uchun {fan} fanidan bitta test savol ber {til}.
Faqat JSON formatda yoz, boshqa hech narsa yozma:
{{"savol": "savol matni", "A": "variant", "B": "variant", "C": "variant", "D": "variant", "togri": "A"}}"""
    text = await groq_request(prompt)
    try:
        text = text.strip().replace("```json", "").replace("```", "")
        return json.loads(text)
    except:
        return None

async def insho_tekshir(matn: str, mavzu: str, sinf: str, lang: str, ism: str = "") -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    ism_korsatma = f"O'quvchining ismi {ism}. Baholashni '{ism}' deb murojaat qilib boshla." if ism else ""
    prompt = f"""Sen AI ustoz botsan. {ism_korsatma}
O'quvchining inshosini tekshir {til}.
O'quvchi sinfi: {sinf}
Mavzu: {mavzu}
Insho:
{matn}
Baho ber (1-10), kuchli va zaif tomonlarini ayt, tavsiyalar ber."""
    return await groq_request(prompt)
