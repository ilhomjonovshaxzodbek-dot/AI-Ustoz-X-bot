from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.main_kb import main_keyboard, bekor_keyboard, TEXTS
from database import get_db
from utils.gemini import savol_javob

router = Router()

class SavolState(StatesGroup):
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
        [InlineKeyboardButton(text="📝 Qisqa javob", callback_data="uzun_qisqa")],
        [InlineKeyboardButton(text="📖 Batafsil javob", callback_data="uzun_uzun")],
    ])

@router.message(F.text.in_([
    TEXTS["uz"]["savol"], TEXTS["ru"]["savol"], TEXTS["en"]["savol"]
]))
async def savol_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user or not user["sinf"]:
        await message.answer("⚠️ Avval sinf/kursni tanlang!")
        return
    lang = user["lang"]
    await state.set_state(SavolState.kutish)
    await message.answer(
        "❓ Savolingizni yozing:" if lang == "uz" else "❓ Напишите ваш вопрос:" if lang == "ru" else "❓ Write your question:",
        reply_markup=bekor_keyboard(lang)
    )

@router.message(SavolState.kutish)
async def savol_javob_handler(message: Message, state: FSMContext):
    await state.update_data(savol=message.text)
    await state.set_state(SavolState.uzunlik_kutish)
    await message.answer(
        "📏 Javob qanday bo'lsin?",
        reply_markup=uzunlik_keyboard()
    )

@router.callback_query(F.data.startswith("uzun_"), SavolState.uzunlik_kutish)
async def uzunlik_tanlash(call: CallbackQuery, state: FSMContext):
    uzun = call.data == "uzun_uzun"
    user = get_user(call.from_user.id)
    lang = user["lang"]
    sinf = user["sinf"]
    ism = user["ism"] or ""
    data = await state.get_data()
    savol = data["savol"]
    
    await call.message.edit_text("⏳ Javob tayyorlanmoqda..." if lang == "uz" else "⏳ Готовлю ответ..." if lang == "ru" else "⏳ Preparing answer...")
    
    javob = await savol_javob(savol, sinf, lang, ism, uzun)
    await state.clear()
    await call.message.edit_text(javob)
    await call.message.answer("📋 Menyu:", reply_markup=main_keyboard(lang))
