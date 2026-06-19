from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.main_kb import main_keyboard, bekor_keyboard, TEXTS
from database import get_db
from utils.gemini import tushuntir

router = Router()

class TushuntirState(StatesGroup):
    kutish = State()
    uzunlik_kutish = State()

def get_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    return user

def uzunlik_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Qisqa javob", callback_data="tuzun_qisqa")],
        [InlineKeyboardButton(text="📖 Batafsil javob", callback_data="tuzun_uzun")],
    ])

@router.message(F.text.in_([
    TEXTS["uz"]["tushuntir"], TEXTS["ru"]["tushuntir"], TEXTS["en"]["tushuntir"]
]))
async def tushuntir_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user or not user["sinf"]:
        await message.answer("⚠️ Avval sinf/kursni tanlang!")
        return
    lang = user["lang"]
    await state.set_state(TushuntirState.kutish)
    await message.answer(
        "📖 Qaysi mavzuni tushuntiray?" if lang == "uz" else "📖 Какую тему объяснить?" if lang == "ru" else "📖 What topic to explain?",
        reply_markup=bekor_keyboard(lang)
    )

@router.message(TushuntirState.kutish)
async def tushuntir_mavzu_handler(message: Message, state: FSMContext):
    await state.update_data(mavzu=message.text)
    await state.set_state(TushuntirState.uzunlik_kutish)
    await message.answer(
        "📏 Tushuntirish qanday bo'lsin?",
        reply_markup=uzunlik_keyboard()
    )

@router.callback_query(F.data.startswith("tuzun_"), TushuntirState.uzunlik_kutish)
async def tuzunlik_tanlash(call: CallbackQuery, state: FSMContext):
    uzun = call.data == "tuzun_uzun"
    user = get_user(call.from_user.id)
    lang = user["lang"]
    sinf = user["sinf"]
    ism = user["ism"] or ""
    data = await state.get_data()
    mavzu = data["mavzu"]
    
    await call.message.edit_text("⏳ Tushuntirilmoqda..." if lang == "uz" else "⏳ Объясняю..." if lang == "ru" else "⏳ Explaining...")
    
    javob = await tushuntir(mavzu, sinf, lang, ism, uzun)
    await state.clear()
    await call.message.edit_text(javob)
    await call.message.answer("📋 Menyu:", reply_markup=main_keyboard(lang))
