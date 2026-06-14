from aiogram import Router, F
from aiogram.types import Message
from keyboards.main_kb import main_keyboard, TEXTS
from database import get_db

router = Router()

def get_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    return user

@router.message(F.text.in_([
    TEXTS["uz"]["reyting"], TEXTS["ru"]["reyting"], TEXTS["en"]["reyting"]
]))
async def reyting_handler(message: Message):
    user = get_user(message.from_user.id)
    lang = user["lang"]
    
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT u.name, u.tg_id,
               COALESCE((SELECT SUM(togri) FROM masalalar WHERE user_id = u.tg_id), 0) +
               COALESCE((SELECT SUM(togri) FROM testlar WHERE user_id = u.tg_id), 0) as ball
        FROM users u
        ORDER BY ball DESC
        LIMIT 10
    """)
    top = cur.fetchall()
    db.close()
    
    medals = ["🥇", "🥈", "🥉"]
    
    if lang == "uz":
        text = "🏆 *Top 10 o'quvchilar*\n\n"
    elif lang == "ru":
        text = "🏆 *Топ 10 учеников*\n\n"
    else:
        text = "🏆 *Top 10 Students*\n\n"
    
    for i, row in enumerate(top):
        medal = medals[i] if i < 3 else f"{i+1}."
        name = row["name"] or "Noma'lum"
        ball = row["ball"]
        marker = " 👈" if row["tg_id"] == message.from_user.id else ""
        text += f"{medal} {name} — {ball} ball{marker}\n"
    
    await message.answer(text, parse_mode="Markdown", reply_markup=main_keyboard(lang))
