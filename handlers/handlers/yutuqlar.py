from aiogram import Router, F, Bot
from aiogram.types import Message
from keyboards.main_kb import main_keyboard, TEXTS
from database import get_db

router = Router()

YUTUQLAR = [
    {"nomi": "🌱 Yangi boshlovchi", "tavsif": "Birinchi masalani yechdingiz!", "ball": 1},
    {"nomi": "⭐ Faol o'quvchi", "tavsif": "10 ta masala yechdingiz!", "ball": 10},
    {"nomi": "🔥 Izlanuvchi", "tavsif": "25 ta masala yechdingiz!", "ball": 25},
    {"nomi": "💎 Bilim ustasi", "tavsif": "50 ta masala yechdingiz!", "ball": 50},
    {"nomi": "🏆 Champion", "tavsif": "100 ta masala yechdingiz!", "ball": 100},
    {"nomi": "🎯 Test ustasi", "tavsif": "10 ta testni to'g'ri yechdingiz!", "ball": 10, "tur": "test"},
    {"nomi": "🚀 Super o'quvchi", "tavsif": "50 ta testni to'g'ri yechdingiz!", "ball": 50, "tur": "test"},
]

def get_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    return user

async def yutuq_tekshir(bot: Bot, user_id: int):
    db = get_db()
    cur = db.cursor()
    
    cur.execute("SELECT COUNT(*) as soni, SUM(togri) as togri FROM masalalar WHERE user_id = ?", (user_id,))
    masala_stat = cur.fetchone()
    
    cur.execute("SELECT COUNT(*) as soni, SUM(togri) as togri FROM testlar WHERE user_id = ?", (user_id,))
    test_stat = cur.fetchone()
    
    cur.execute("SELECT nomi FROM yutuqlar WHERE user_id = ?", (user_id,))
    mavjud_yutuqlar = [r["nomi"] for r in cur.fetchall()]
    
    user = get_user(user_id)
    lang = user["lang"] if user else "uz"
    
    yangi_yutuqlar = []
    
    for y in YUTUQLAR:
        if y["nomi"] in mavjud_yutuqlar:
            continue
        
        tur = y.get("tur", "masala")
        if tur == "masala":
            togri = masala_stat["togri"] or 0
        else:
            togri = test_stat["togri"] or 0
        
        if togri >= y["ball"]:
            cur.execute(
                "INSERT INTO yutuqlar (user_id, nomi, tavsif) VALUES (?, ?, ?)",
                (user_id, y["nomi"], y["tavsif"])
            )
            yangi_yutuqlar.append(y)
    
    db.commit()
    
    if yangi_yutuqlar:
        cur.execute("SELECT tg_id FROM users", )
        barcha_users = cur.fetchall()
        db.close()
        
        for y in yangi_yutuqlar:
            xabar = (
                f"🎉 *Yangi yutuq!*\n\n"
                f"*{user['name']}* yangi yutuq qo'lga kiritdi:\n"
                f"{y['nomi']} — {y['tavsif']}"
            )
            for u in barcha_users:
                try:
                    await bot.send_message(u["tg_id"], xabar, parse_mode="Markdown")
                except:
                    pass
    else:
        db.close()

@router.message(F.text.in_([
    TEXTS["uz"]["yutuqlar"], TEXTS["ru"]["yutuqlar"], TEXTS["en"]["yutuqlar"]
]))
async def yutuqlar_handler(message: Message):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM yutuqlar WHERE user_id = ? ORDER BY sana DESC", (message.from_user.id,))
    yutuqlar = cur.fetchall()
    db.close()
    
    if not yutuqlar:
        text = {
            "uz": "🏅 Hali yutuq yo'q!\n\nMasala yechib, test ishlab yutuq qo'lga kiriting!",
            "ru": "🏅 Пока нет достижений!\n\nРешайте задачи и тесты чтобы получить достижения!",
            "en": "🏅 No achievements yet!\n\nSolve tasks and tests to earn achievements!"
        }.get(lang, "🏅 Hali yutuq yo'q!")
    else:
        if lang == "uz":
            text = f"🏅 *Mening yutuqlarim* ({len(yutuqlar)} ta)\n\n"
        elif lang == "ru":
            text = f"🏅 *Мои достижения* ({len(yutuqlar)})\n\n"
        else:
            text = f"🏅 *My Achievements* ({len(yutuqlar)})\n\n"
        
        for y in yutuqlar:
            text += f"{y['nomi']}\n_{y['tavsif']}_\n\n"
    
    await message.answer(text, parse_mode="Markdown", reply_markup=main_keyboard(lang))
