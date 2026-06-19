from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.main_kb import main_keyboard, bekor_keyboard, TEXTS
from database import get_db
from utils.gemini import insho_tekshir

router = Router()

class InshoState(StatesGroup):
    mavzu_kutish = State()
    matn_kutish = State()

def get_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    return user

@router.message(F.text.in_([
    TEXTS["uz"]["insho"], TEXTS["ru"]["insho"], TEXTS["en"]["insho"]
]))
async def insho_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user or not user["sinf"]:
        await message.answer("⚠️ Avval sinf/kursni tanlang!")
        return
    lang = user["lang"]
    await state.set_state(InshoState.mavzu_kutish)
    await message.answer(
        "📝 Insho mavzusini yozing:" if lang == "uz" else "📝 Напишите тему сочинения:" if lang == "ru" else "📝 Write the essay topic:",
        reply_markup=bekor_keyboard(lang)
    )

@router.message(InshoState.mavzu_kutish)
async def mavzu_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["lang"]
    await state.update_data(mavzu=message.text)
    await state.set_state(InshoState.matn_kutish)
    await message.answer(
        "✏️ Inshoingizni yozing:" if lang == "uz" else "✏️ Напишите ваше сочинение:" if lang == "ru" else "✏️ Write your essay:",
        reply_markup=bekor_keyboard(lang)
    )

@router.message(InshoState.matn_kutish)
async def matn_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["lang"]
    sinf = user["sinf"]
    ism = user["ism"] or ""
    data = await state.get_data()
    mavzu = data.get("mavzu")
    await message.answer("⏳ Tekshirilmoqda..." if lang == "uz" else "⏳ Проверяю..." if lang == "ru" else "⏳ Checking...")
    natija = await insho_tekshir(message.text, mavzu, sinf, lang, ism)
    await state.clear()
    await message.answer(natija, reply_markup=main_keyboard(lang))
