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
    TEXTS["uz"]["natija"], TEXTS["ru"]["natija"], TEXTS["en"]["natija"]
]))
async def natijalar_handler(message: Message):
    user = get_user(message.from_user.id)
    lang = user["lang"]
    
    db = get_db()
    cur = db.cursor()
    
    cur.execute("SELECT COUNT(*), SUM(togri) FROM masalalar WHERE user_id = ?", (message.from_user.id,))
    masala_stat = cur.fetchone()
    
    cur.execute("SELECT COUNT(*), SUM(togri) FROM testlar WHERE user_id = ?", (message.from_user.id,))
    test_stat = cur.fetchone()
    db.close()
    
    masala_jami = masala_stat[0] or 0
    masala_togri = masala_stat[1] or 0
    test_jami = test_stat[0] or 0
    test_togri = test_stat[1] or 0
    
    if lang == "uz":
        text = (
            f"📊 *Mening natijalarim*\n\n"
            f"📚 Masalalar: {masala_togri}/{masala_jami} to'g'ri\n"
            f"🎯 Testlar: {test_togri}/{test_jami} to'g'ri\n"
            f"🏆 Jami ball: {masala_togri + test_togri}"
        )
    elif lang == "ru":
        text = (
            f"📊 *Мои результаты*\n\n"
            f"📚 Задачи: {masala_togri}/{masala_jami} правильно\n"
            f"🎯 Тесты: {test_togri}/{test_jami} правильно\n"
            f"🏆 Всего баллов: {masala_togri + test_togri}"
        )
    else:
        text = (
            f"📊 *My Results*\n\n"
            f"📚 Tasks: {masala_togri}/{masala_jami} correct\n"
            f"🎯 Tests: {test_togri}/{test_jami} correct\n"
            f"🏆 Total score: {masala_togri + test_togri}"
        )
    
    await message.answer(text, parse_mode="Markdown", reply_markup=main_keyboard(lang))
