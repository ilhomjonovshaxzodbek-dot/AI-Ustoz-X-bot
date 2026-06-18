from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from keyboards.inline_kb import lang_keyboard, sinf_keyboard, kurs_keyboard
from keyboards.main_kb import main_keyboard, TEXTS
from database import get_db

router = Router()

BEKOR_TEXTLAR = ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]

async def send_lang_menu(message: Message, user_id: int):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT lang, sinf FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    
    if user and user["lang"] and user["sinf"]:
        lang = user["lang"]
        await message.answer(
            "✅ Xush kelibsiz!" if lang == "uz" else "✅ Добро пожаловать!" if lang == "ru" else "✅ Welcome!",
            reply_markup=main_keyboard(lang)
        )
        return
    
    await message.answer(
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=lang_keyboard()
    )

@router.message(F.text.in_(BEKOR_TEXTLAR))
async def global_bekor_handler(message: Message, state: FSMContext):
    from aiogram.fsm.context import FSMContext
    user_id = message.from_user.id
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT lang FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    lang = user["lang"] if user else "uz"
    
    await state.clear()
    await message.answer(
        "❌ Bekor qilindi." if lang == "uz" else "❌ Отменено." if lang == "ru" else "❌ Cancelled.",
        reply_markup=main_keyboard(lang)
    )

@router.message(CommandStart())
async def start_handler(message: Message):
    user = message.from_user
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (tg_id, name) VALUES (?, ?)",
        (user.id, user.full_name)
    )
    db.commit()
    db.close()
    await send_lang_menu(message, user.id)

@router.callback_query(F.data.startswith("lang_"))
async def lang_handler(call: CallbackQuery):
    lang = call.data.split("_")[1]
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE users SET lang = ? WHERE tg_id = ?", (lang, call.from_user.id))
    db.commit()
    db.close()
    
    await call.message.edit_text(
        "🎓 Sinfingizni tanlang:" if lang == "uz" else "🎓 Выберите класс:" if lang == "ru" else "🎓 Choose your class:",
        reply_markup=sinf_keyboard()
    )

@router.callback_query(F.data.startswith("sinf_"))
async def sinf_handler(call: CallbackQuery):
    sinf = call.data.split("_")[1]
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT lang FROM users WHERE tg_id = ?", (call.from_user.id,))
    user = cur.fetchone()
    lang = user["lang"] if user else "uz"
    
    if sinf == "talaba":
        cur.execute("UPDATE users SET type = 'talaba' WHERE tg_id = ?", (call.from_user.id,))
        db.commit()
        db.close()
        await call.message.edit_text(
            "📚 Kursni tanlang:" if lang == "uz" else "📚 Выберите курс:" if lang == "ru" else "📚 Choose your course:",
            reply_markup=kurs_keyboard()
        )
    else:
        cur.execute(
            "UPDATE users SET sinf = ?, type = 'maktab' WHERE tg_id = ?",
            (f"{sinf}-sinf", call.from_user.id)
        )
        db.commit()
        db.close()
        await call.message.delete()
        await call.message.answer(
            "✅ Ajoyib! Endi o'qishni boshlaylik!" if lang == "uz" else "✅ Отлично! Начнём учиться!" if lang == "ru" else "✅ Great! Let's start learning!",
            reply_markup=main_keyboard(lang)
        )

@router.callback_query(F.data.startswith("kurs_"))
async def kurs_handler(call: CallbackQuery):
    kurs = call.data.split("_")[1]
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT lang FROM users WHERE tg_id = ?", (call.from_user.id,))
    user = cur.fetchone()
    lang = user["lang"] if user else "uz"
    cur.execute(
        "UPDATE users SET sinf = ? WHERE tg_id = ?",
        (f"{kurs}-kurs", call.from_user.id)
    )
    db.commit()
    db.close()
    await call.message.delete()
    await call.message.answer(
        "✅ Ajoyib! Endi o'qishni boshlaylik!" if lang == "uz" else "✅ Отлично! Начнём учиться!" if lang == "ru" else "✅ Great! Let's start learning!",
        reply_markup=main_keyboard(lang)
    )
