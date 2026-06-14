from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.main_kb import main_keyboard, sozlamalar_keyboard, TEXTS
from keyboards.inline_kb import lang_keyboard, sinf_keyboard
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
    TEXTS["uz"]["sozlama"], TEXTS["ru"]["sozlama"], TEXTS["en"]["sozlama"]
]))
async def sozlamalar_handler(message: Message):
    user = get_user(message.from_user.id)
    lang = user["lang"]
    await message.answer(
        "⚙️ Sozlamalar:" if lang == "uz" else "⚙️ Настройки:" if lang == "ru" else "⚙️ Settings:",
        reply_markup=sozlamalar_keyboard(lang)
    )

@router.message(F.text.in_(["🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Change Language"]))
async def til_ozgartir(message: Message):
    await message.answer(
        "🌐 Tilni tanlang:" if True else "",
        reply_markup=lang_keyboard()
    )

@router.message(F.text.in_(["🎓 Sinf/Kursni o'zgartirish", "🎓 Сменить класс/курс", "🎓 Change Class/Course"]))
async def sinf_ozgartir(message: Message):
    user = get_user(message.from_user.id)
    lang = user["lang"]
    await message.answer(
        "🎓 Sinfingizni tanlang:" if lang == "uz" else "🎓 Выберите класс:" if lang == "ru" else "🎓 Choose class:",
        reply_markup=sinf_keyboard()
    )

@router.message(F.text.in_(["🔙 Orqaga", "🔙 Назад", "🔙 Back"]))
async def orqaga(message: Message):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    await message.answer(
        "📋 Menyu:" if lang == "uz" else "📋 Меню:" if lang == "ru" else "📋 Menu:",
        reply_markup=main_keyboard(lang)
    )
