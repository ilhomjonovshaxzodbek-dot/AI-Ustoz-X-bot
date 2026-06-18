from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline_kb import fan_keyboard
from keyboards.main_kb import main_keyboard, bekor_keyboard, TEXTS
from database import get_db
from utils.gemini import masala_ber, javob_tekshir

router = Router()

class MasalaState(StatesGroup):
    fan_tanlash = State()
    javob_kutish = State()

def get_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    return user

@router.message(F.text.in_([
    TEXTS["uz"]["masala"], TEXTS["ru"]["masala"], TEXTS["en"]["masala"]
]))
async def masala_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user or not user["sinf"]:
        await message.answer("⚠️ Avval sinf/kursni tanlang!")
        return
    lang = user["lang"]
    await state.set_state(MasalaState.fan_tanlash)
    await message.answer(
        "📚 Fan tanlang:" if lang == "uz" else "📚 Выберите предмет:" if lang == "ru" else "📚 Choose subject:",
        reply_markup=bekor_keyboard(lang)
    )
    await message.answer(
        "👇 Fanni tanlang:" if lang == "uz" else "👇 Выберите предмет:" if lang == "ru" else "👇 Choose subject:",
        reply_markup=fan_keyboard(lang)
    )

@router.callback_query(F.data.startswith("fan_"), MasalaState.fan_tanlash)
async def fan_tanlash_handler(call: CallbackQuery, state: FSMContext):
    fan = call.data.split("_", 1)[1]
    user = get_user(call.from_user.id)
    lang = user["lang"]
    sinf = user["sinf"]
    await call.message.edit_text("⏳ Masala tayyorlanmoqda..." if lang == "uz" else "⏳ Готовлю задачу..." if lang == "ru" else "⏳ Preparing task...")
    masala = await masala_ber(sinf, fan, lang)
    await state.update_data(masala=masala, fan=fan)
    await state.set_state(MasalaState.javob_kutish)
    await call.message.edit_text(
        f"📚 *{fan}* | {sinf}\n\n{masala}\n\n"
        + ("✏️ Javobingizni yozing:" if lang == "uz" else "✏️ Напишите ответ:" if lang == "ru" else "✏️ Write your answer:"),
        parse_mode="Markdown"
    )

@router.message(MasalaState.javob_kutish)
async def javob_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["lang"]
    sinf = user["sinf"]
    data = await state.get_data()
    masala = data.get("masala")
    await message.answer("⏳ Tekshirilmoqda..." if lang == "uz" else "⏳ Проверяю..." if lang == "ru" else "⏳ Checking...")
    natija = await javob_tekshir(masala, message.text, sinf, lang)
    db = get_db()
    cur = db.cursor()
    togri = 1 if "to'g'ri" in natija.lower() or "правильно" in natija.lower() or "correct" in natija.lower() else 0
    cur.execute("INSERT INTO masalalar (user_id, masala, javob, togri) VALUES (?, ?, ?, ?)",
                (message.from_user.id, masala, message.text, togri))
    db.commit()
    db.close()
    await state.clear()
    await message.answer(natija, reply_markup=main_keyboard(lang))
    from handlers.yutuqlar import yutuq_tekshir
    await yutuq_tekshir(message.bot, message.from_user.id)
