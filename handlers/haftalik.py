from aiogram import Router, F, Bot
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
    TEXTS["uz"]["haftalik"], TEXTS["ru"]["haftalik"], TEXTS["en"]["haftalik"]
]))
async def haftalik_handler(message: Message):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT u.name, u.tg_id,
               COALESCE((SELECT COUNT(*) FROM masalalar WHERE user_id = u.tg_id AND sana >= date('now', '-7 days')), 0) +
               COALESCE((SELECT COUNT(*) FROM testlar WHERE user_id = u.tg_id AND sana >= date('now', '-7 days')), 0) as haftalik_ball
        FROM users u
        ORDER BY haftalik_ball DESC
        LIMIT 10
    """)
    top = cur.fetchall()
    db.close()
    
    medals = ["🥇", "🥈", "🥉"]
    
    if lang == "uz":
        text = "📈 *Bu hafta eng ko'p o'qiganlar*\n\n"
    elif lang == "ru":
        text = "📈 *Самые активные на этой неделе*\n\n"
    else:
        text = "📈 *Most Active This Week*\n\n"
    
    for i, row in enumerate(top):
        medal = medals[i] if i < 3 else f"{i+1}."
        name = row["name"] or "Noma'lum"
        ball = row["haftalik_ball"]
        marker = " 👈" if row["tg_id"] == message.from_user.id else ""
        text += f"{medal} {name} — {ball} ta{marker}\n"
    
    if not any(row["tg_id"] == message.from_user.id for row in top):
        cur2 = get_db().cursor()
        cur2.execute("""
            SELECT COALESCE((SELECT COUNT(*) FROM masalalar WHERE user_id = ? AND sana >= date('now', '-7 days')), 0) +
                   COALESCE((SELECT COUNT(*) FROM testlar WHERE user_id = ? AND sana >= date('now', '-7 days')), 0) as ball
        """, (message.from_user.id, message.from_user.id))
        my = cur2.fetchone()
        text += f"\n👤 Siz: {my['ball']} ta" if lang == "uz" else f"\n👤 Вы: {my['ball']}" if lang == "ru" else f"\n👤 You: {my['ball']}"
    
    await message.answer(text, parse_mode="Markdown", reply_markup=main_keyboard(lang))

async def haftalik_yuborish(bot: Bot):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT u.tg_id, u.name, u.lang,
               COALESCE((SELECT COUNT(*) FROM masalalar WHERE user_id = u.tg_id AND sana >= date('now', '-7 days')), 0) +
               COALESCE((SELECT COUNT(*) FROM testlar WHERE user_id = u.tg_id AND sana >= date('now', '-7 days')), 0) as ball
        FROM users u
    """)
    users = cur.fetchall()
    
    cur.execute("""
        SELECT u.name, u.tg_id,
               COALESCE((SELECT COUNT(*) FROM masalalar WHERE user_id = u.tg_id AND sana >= date('now', '-7 days')), 0) +
               COALESCE((SELECT COUNT(*) FROM testlar WHERE user_id = u.tg_id AND sana >= date('now', '-7 days')), 0) as ball
        FROM users u
        ORDER BY ball DESC
        LIMIT 3
    """)
    top3 = cur.fetchall()
    db.close()
    
    if not top3:
        return
    
    top_text = "\n".join([f"{'🥇🥈🥉'[i]} {r['name']} — {r['ball']} ta" for i, r in enumerate(top3)])
    
    for u in users:
        lang = u["lang"] or "uz"
        if lang == "uz":
            text = f"📈 *Haftalik hisobot!*\n\n🏆 Bu hafta eng faollar:\n{top_text}\n\nSizning ballingiz: *{u['ball']}* ta"
        elif lang == "ru":
            text = f"📈 *Еженедельный отчёт!*\n\n🏆 Самые активные:\n{top_text}\n\nВаш результат: *{u['ball']}*"
        else:
            text = f"📈 *Weekly Report!*\n\n🏆 Most Active:\n{top_text}\n\nYour score: *{u['ball']}*"
        
        try:
            await bot.send_message(u["tg_id"], text, parse_mode="Markdown")
        except:
            pass
