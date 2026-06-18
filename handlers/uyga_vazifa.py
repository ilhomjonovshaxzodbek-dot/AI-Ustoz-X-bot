from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline_kb import fan_keyboard
from keyboards.main_kb import main_keyboard, bekor_keyboard, TEXTS
from database import get_db
from utils.gemini import groq_request

router = Router()

class UygaVazifaState(StatesGroup):
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
    TEXTS["uz"]["uyga_vazifa"], TEXTS["ru"]["uyga_vazifa"], TEXTS["en"]["uyga_vazifa"]
]))
async def uyga_vazifa_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user or not user["sinf"]:
        await message.answer("⚠️ Avval sinf/kursni tanlang!")
        return
    lang = user["lang"]
    await state.set_state(UygaVazifaState.fan_tanlash)
    await message.answer(
        "📋 Qaysi fandan uyga vazifa olasiz?" if lang == "uz" else "📋 По какому предмету домашнее задание?" if lang == "ru" else "📋 Which subject for homework?",
        reply_markup=bekor_keyboard(lang)
    )
    await message.answer(
        "👇 Fanni tanlang:" if lang == "uz" else "👇 Выберите предмет:" if lang == "ru" else "👇 Choose subject:",
        reply_markup=fan_keyboard(lang)
    )

@router.message(F.text.in_(["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]), UygaVazifaState.fan_tanlash)
async def uyga_bekor_fan(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    await state.clear()
    await message.answer(
        "❌ Bekor qilindi." if lang == "uz" else "❌ Отменено." if lang == "ru" else "❌ Cancelled.",
        reply_markup=main_keyboard(lang)
    )

@router.message(F.text.in_(["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]), UygaVazifaState.javob_kutish)
async def uyga_bekor_javob(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    await state.clear()
    await message.answer(
        "❌ Bekor qilindi." if lang == "uz" else "❌ Отменено." if lang == "ru" else "❌ Cancelled.",
        reply_markup=main_keyboard(lang)
    )

@router.callback_query(F.data.startswith("fan_"), UygaVazifaState.fan_tanlash)
async def uyga_fan_handler(call: CallbackQuery, state: FSMContext):
    fan = call.data.split("_", 1)[1]
    user = get_user(call.from_user.id)
    lang = user["lang"]
    sinf = user["sinf"]
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    
    await call.message.edit_text(
        "⏳ Uyga vazifa tayyorlanmoqda..." if lang == "uz" else "⏳ Готовлю домашнее задание..." if lang == "ru" else "⏳ Preparing homework..."
    )
    
    prompt = f"""Sen AI ustoz botsan. {sinf} uchun {fan} fanidan uyga vazifa ber {til}.
Vazifa qiziqarli va o'quvchinning darajasiga mos bo'lsin.
3-5 ta topshiriq ber. Har bir topshiriq raqamlangan bo'lsin.
Faqat vazifani yoz, javobini yozma."""
    
    vazifa = await groq_request(prompt)
    
    await state.update_data(fan=fan, sinf=sinf, vazifa=vazifa)
    await state.set_state(UygaVazifaState.javob_kutish)
    
    await call.message.edit_text(
        f"📋 *Uyga vazifa* | {fan} | {sinf}\n\n{vazifa}\n\n"
        + ("✏️ Vazifani bajaring va yuboring:" if lang == "uz" else "✏️ Выполните задание и отправьте:" if lang == "ru" else "✏️ Complete and send your work:"),
        parse_mode="Markdown"
    )

@router.message(UygaVazifaState.javob_kutish)
async def uyga_javob_handler(message: Message, state: FSMContext):
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
    data = await state.get_data()
    fan = data["fan"]
    vazifa = data["vazifa"]
    til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
    
    await message.answer(
        "⏳ Tekshirilmoqda..." if lang == "uz" else "⏳ Проверяю..." if lang == "ru" else "⏳ Checking..."
    )
    
    prompt = f"""Sen AI ustoz botsan. O'quvchining uyga vazifasini tekshir {til}.

Vazifa:
{vazifa}

O'quvchi javobi:
{message.text}

Quyidagilarni yoz:
1. Har bir topshiriq uchun to'g'ri/noto'g'ri
2. Xatolar haqida tushuntirish
3. Umumiy baho (1-10)
4. Rag'batlantiruvchi so'z"""
    
    natija = await groq_request(prompt)
    
    await state.clear()
    await message.answer(
        f"📋 *Uyga vazifa natijasi* | {fan}\n\n{natija}",
        parse_mode="Markdown",
        reply_markup=main_keyboard(lang)
    )
