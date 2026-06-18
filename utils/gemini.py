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
    chaqirish = f"{ism}," if ism else ""
    prompt = f"Sen AI ustoz botsan. {chaqirish} {sinf} uchun {fan} fanidan bitta masala/misol ber {til}. Faqat masalani yoz, javobini yozma. Masala qisqa va tushunarli bo'lsin."
    return await groq_request(prompt)

async def javob_tekshir(masala: str, foydalanuvchi_javobi: str, sinf: str, lang: str, ism: str = "") -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    chaqirish = f"{ism}," if ism else ""
    prompt = f"Sen AI ustoz botsan. {chaqirish} quyidagi masalani tekshir {til}:\nMasala: {masala}\nO'quvchi javobi: {foydalanuvchi_javobi}\nO'quvchi sinfi: {sinf}\nJavob to'g'rimi yoki noto'g'rimi ayt. Agar noto'g'ri bo'lsa to'g'ri yechimni bosqichma-bosqich tushuntir."
    return await groq_request(prompt)

async def savol_javob(savol: str, sinf: str, lang: str, ism: str = "", uzun: bool = False) -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    chaqirish = f"{ism}," if ism else ""
    uzunlik = "batafsil va to'liq" if uzun else "qisqa va aniq"
    prompt = f"Sen AI ustoz botsan. {chaqirish} O'quvchi savol berdi {til}.\nO'quvchi sinfi: {sinf}\nSavol: {savol}\n{uzunlik} tushuntir. Kerak bo'lsa misol keltir."
    return await groq_request(prompt)

async def tushuntir(mavzu: str, sinf: str, lang: str, ism: str = "", uzun: bool = False) -> str:
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    chaqirish = f"{ism}," if ism else ""
    uzunlik = "batafsil va to'liq" if uzun else "qisqa va aniq"
    prompt = f"Sen AI ustoz botsan. {chaqirish} quyidagi mavzuni {sinf} o'quvchisiga {til} {uzunlik} tushuntir:\nMavzu: {mavzu}\nMisol keltir."
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
    chaqirish = f"{ism}," if ism else ""
    prompt = f"Sen AI ustoz botsan. {chaqirish} o'quvchining inshosini tekshir {til}.\nO'quvchi sinfi: {sinf}\nMavzu: {mavzu}\nInsho:\n{matn}\nBaho ber (1-10), kuchli va zaif tomonlarini ayt, tavsiyalar ber."
    return await groq_request(prompt)
