from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.main_kb import main_keyboard, bekor_keyboard, TEXTS
from database import get_db
from utils.gemini import tushuntir

router = Router()

class TushuntirState(StatesGroup):
    kutish = State()

def get_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    return user

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
async def tushuntir_javob_handler(message: Message, state: FSMContext):
    if message.text in ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]:
        user = get_user(message.from_user.id)
        lang = user["lang"] if user else "uz"
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi." if lang == "uz" else "❌ Отменено." if lang == "ru" else "❌ Cancelled.",
            reply_markup=main_keyboard(lang)
        )
        return
    
    user = get_user(message.from_user.id)
    lang = user["lang"]
    sinf = user["sinf"]
    
    await message.answer("⏳ Tushuntirilmoqda..." if lang == "uz" else "⏳ Объясняю..." if lang == "ru" else "⏳ Explaining...")
    
    javob = await tushuntir(message.text, sinf, lang)
    await state.clear()
    await message.answer(javob, reply_markup=main_keyboard(lang))
