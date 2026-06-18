from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline_kb import lang_keyboard, sinf_keyboard, kurs_keyboard
from keyboards.main_kb import main_keyboard, TEXTS
from database import get_db

router = Router()

class RegistratsiyaState(StatesGroup):
    ism_kutish = State()
    familya_kutish = State()

async def send_lang_menu(message: Message, user_id: int):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT lang, sinf, ism, familya FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    
    if user and user["lang"] and user["sinf"] and user["ism"]:
        lang = user["lang"]
        ism = user["ism"]
        familya = user["familya"] or ""
        await message.answer(
            f"✅ Xush kelibsiz, *{ism} {familya}*!" if lang == "uz" 
            else f"✅ Добро пожаловать, *{ism} {familya}*!" if lang == "ru" 
            else f"✅ Welcome, *{ism} {familya}*!",
            parse_mode="Markdown",
            reply_markup=main_keyboard(lang)
        )
        return
    
    await message.answer(
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=lang_keyboard()
    )

@router.message(F.text.in_(["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]))
async def global_bekor_handler(message: Message, state: FSMContext):
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
    cur.execute("INSERT OR IGNORE INTO users (tg_id, name) VALUES (?, ?)", (user.id, user.full_name))
    db.commit()
    db.close()
    await send_lang_menu(message, user.id)

@router.callback_query(F.data.startswith("lang_"))
async def lang_handler(call: CallbackQuery, state: FSMContext):
    lang = call.data.split("_")[1]
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE users SET lang = ? WHERE tg_id = ?", (lang, call.from_user.id))
    cur.execute("SELECT ism FROM users WHERE tg_id = ?", (call.from_user.id,))
    user = cur.fetchone()
    db.commit()
    db.close()
    
    if user and user["ism"]:
        await call.message.edit_text(
            "🎓 Sinfingizni tanlang:" if lang == "uz" else "🎓 Выберите класс:" if lang == "ru" else "🎓 Choose your class:",
            reply_markup=sinf_keyboard()
        )
        return
    
    await state.set_state(RegistratsiyaState.ism_kutish)
    await state.update_data(lang=lang)
    await call.message.edit_text(
        "👤 Ismingizni kiriting:" if lang == "uz" else "👤 Введите ваше имя:" if lang == "ru" else "👤 Enter your name:"
    )

@router.message(RegistratsiyaState.ism_kutish)
async def ism_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    ism = message.text.strip()
    
    if len(ism) < 2:
        await message.answer(
            "❌ Ism juda qisqa! Qayta kiriting:" if lang == "uz" else "❌ Имя слишком короткое! Введите снова:" if lang == "ru" else "❌ Name too short! Enter again:"
        )
        return
    
    await state.update_data(ism=ism)
    await state.set_state(RegistratsiyaState.familya_kutish)
    await message.answer(
        "👤 Familyangizni kiriting:" if lang == "uz" else "👤 Введите вашу фамилию:" if lang == "ru" else "👤 Enter your surname:"
    )

@router.message(RegistratsiyaState.familya_kutish)
async def familya_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    ism = data.get("ism")
    familya = message.text.strip()
    
    if len(familya) < 2:
        await message.answer(
            "❌ Familya juda qisqa! Qayta kiriting:" if lang == "uz" else "❌ Фамилия слишком короткая! Введите снова:" if lang == "ru" else "❌ Surname too short! Enter again:"
        )
        return
    
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE users SET ism = ?, familya = ? WHERE tg_id = ?", (ism, familya, message.from_user.id))
    db.commit()
    db.close()
    
    await state.clear()
    await message.answer(
        f"✅ Salom, *{ism} {familya}*! Endi sinfingizni tanlang:" if lang == "uz"
        else f"✅ Привет, *{ism} {familya}*! Теперь выберите класс:" if lang == "ru"
        else f"✅ Hello, *{ism} {familya}*! Now choose your class:",
        parse_mode="Markdown",
        reply_markup=sinf_keyboard()
    )

@router.callback_query(F.data.startswith("sinf_"))
async def sinf_handler(call: CallbackQuery):
    sinf = call.data.split("_")[1]
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT lang, ism, familya FROM users WHERE tg_id = ?", (call.from_user.id,))
    user = cur.fetchone()
    lang = user["lang"] if user else "uz"
    ism = user["ism"] or ""
    familya = user["familya"] or ""
    
    if sinf == "talaba":
        cur.execute("UPDATE users SET type = 'talaba' WHERE tg_id = ?", (call.from_user.id,))
        db.commit()
        db.close()
        await call.message.edit_text(
            "📚 Kursni tanlang:" if lang == "uz" else "📚 Выберите курс:" if lang == "ru" else "📚 Choose your course:",
            reply_markup=kurs_keyboard()
        )
    else:
        cur.execute("UPDATE users SET sinf = ?, type = 'maktab' WHERE tg_id = ?", (f"{sinf}-sinf", call.from_user.id))
        db.commit()
        db.close()
        await call.message.delete()
        await call.message.answer(
            f"✅ Ajoyib, *{ism} {familya}*! Endi o'qishni boshlaylik!" if lang == "uz"
            else f"✅ Отлично, *{ism} {familya}*! Начнём учиться!" if lang == "ru"
            else f"✅ Great, *{ism} {familya}*! Let's start learning!",
            parse_mode="Markdown",
            reply_markup=main_keyboard(lang)
        )

@router.callback_query(F.data.startswith("kurs_"))
async def kurs_handler(call: CallbackQuery):
    kurs = call.data.split("_")[1]
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT lang, ism, familya FROM users WHERE tg_id = ?", (call.from_user.id,))
    user = cur.fetchone()
    lang = user["lang"] if user else "uz"
    ism = user["ism"] or ""
    familya = user["familya"] or ""
    cur.execute("UPDATE users SET sinf = ? WHERE tg_id = ?", (f"{kurs}-kurs", call.from_user.id))
    db.commit()
    db.close()
    await call.message.delete()
    await call.message.answer(
        f"✅ Ajoyib, *{ism} {familya}*! Endi o'qishni boshlaylik!" if lang == "uz"
        else f"✅ Отлично, *{ism} {familya}*! Начнём учиться!" if lang == "ru"
        else f"✅ Great, *{ism} {familya}*! Let's start learning!",
        parse_mode="Markdown",
        reply_markup=main_keyboard(lang)
    )
