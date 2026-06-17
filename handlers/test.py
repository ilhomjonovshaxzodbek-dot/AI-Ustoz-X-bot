from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline_kb import fan_keyboard
from keyboards.main_kb import main_keyboard, bekor_keyboard, TEXTS
from database import get_db
from utils.gemini import test_ber

router = Router()

class TestState(StatesGroup):
    fan_tanlash = State()
    javob_kutish = State()

def get_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    return user

def test_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="A", callback_data="test_A"),
            InlineKeyboardButton(text="B", callback_data="test_B"),
        ],
        [
            InlineKeyboardButton(text="C", callback_data="test_C"),
            InlineKeyboardButton(text="D", callback_data="test_D"),
        ]
    ])

@router.message(F.text.in_([
    TEXTS["uz"]["test"], TEXTS["ru"]["test"], TEXTS["en"]["test"]
]))
async def test_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user or not user["sinf"]:
        await message.answer("⚠️ Avval sinf/kursni tanlang!")
        return
    lang = user["lang"]
    await state.set_state(TestState.fan_tanlash)
    await message.answer(
        "🎯 Fan tanlang:" if lang == "uz" else "🎯 Выберите предмет:" if lang == "ru" else "🎯 Choose subject:",
        reply_markup=bekor_keyboard(lang)
    )
    await message.answer(
        "👇 Fanni tanlang:" if lang == "uz" else "👇 Выберите предмет:" if lang == "ru" else "👇 Choose subject:",
        reply_markup=fan_keyboard(lang)
    )

@router.callback_query(F.data.startswith("fan_"), TestState.fan_tanlash)
async def test_fan_handler(call: CallbackQuery, state: FSMContext):
    fan = call.data.split("_", 1)[1]
    user = get_user(call.from_user.id)
    lang = user["lang"]
    sinf = user["sinf"]
    
    await call.message.edit_text("⏳ Test tayyorlanmoqda..." if lang == "uz" else "⏳ Готовлю тест..." if lang == "ru" else "⏳ Preparing test...")
    
    test = await test_ber(sinf, fan, lang)
    if not test:
        await call.message.edit_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
        await state.clear()
        return
    
    await state.update_data(test=test, fan=fan)
    await state.set_state(TestState.javob_kutish)
    
    text = (
        f"🎯 *{fan}* | {sinf}\n\n"
        f"{test['savol']}\n\n"
        f"A) {test['A']}\n"
        f"B) {test['B']}\n"
        f"C) {test['C']}\n"
        f"D) {test['D']}"
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=test_keyboard())

@router.message(F.text.in_(["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]), TestState.fan_tanlash)
async def test_bekor_fan(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    await state.clear()
    await message.answer(
        "❌ Bekor qilindi." if lang == "uz" else "❌ Отменено." if lang == "ru" else "❌ Cancelled.",
        reply_markup=main_keyboard(lang)
    )

@router.callback_query(F.data.startswith("test_"), TestState.javob_kutish)
async def test_javob_handler(call: CallbackQuery, state: FSMContext):
    javob = call.data.split("_")[1]
    user = get_user(call.from_user.id)
    lang = user["lang"]
    data = await state.get_data()
    test = data.get("test")
    togri = test["togri"]
    
    db = get_db()
    cur = db.cursor()
    togri_bool = 1 if javob == togri else 0
    cur.execute(
        "INSERT INTO testlar (user_id, savol, togri) VALUES (?, ?, ?)",
        (call.from_user.id, test["savol"], togri_bool)
    )
    db.commit()
    db.close()
    
    if javob == togri:
        text = "✅ To'g'ri!" if lang == "uz" else "✅ Правильно!" if lang == "ru" else "✅ Correct!"
    else:
        text = (
            f"❌ Noto'g'ri! To'g'ri javob: *{togri}*" if lang == "uz"
            else f"❌ Неправильно! Правильный ответ: *{togri}*" if lang == "ru"
            else f"❌ Wrong! Correct answer: *{togri}*"
        )
    
    await state.clear()
    await call.message.edit_text(text, parse_mode="Markdown")
    await call.message.answer("📋 Menyu:", reply_markup=main_keyboard(lang))
    
    from handlers.yutuqlar import yutuq_tekshir
    await yutuq_tekshir(call.bot, call.from_user.id)
