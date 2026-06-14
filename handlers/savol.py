from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.main_kb import main_keyboard, TEXTS
from database import get_db
from utils.gemini import savol_javob

router = Router()

class SavolState(StatesGroup):
    kutish = State()

def get_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    return user

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
        "❓ Savolingizni yozing:" if lang == "uz" else "❓ Напишите ваш вопрос:" if lang == "ru" else "❓ Write your question:"
    )

@router.message(SavolState.kutish)
async def savol_javob_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["lang"]
    sinf = user["sinf"]
    
    await message.answer("⏳ Javob tayyorlanmoqda..." if lang == "uz" else "⏳ Готовлю ответ..." if lang == "ru" else "⏳ Preparing answer...")
    
    javob = await savol_javob(message.text, sinf, lang)
    await state.clear()
    await message.answer(javob, reply_markup=main_keyboard(lang))
