from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.main_kb import main_keyboard, bekor_keyboard, TEXTS
from database import get_db

router = Router()

class SevimliState(StatesGroup):
    tanlash = State()

FANLAR = {
    "uz": ["Matematika", "Fizika", "Kimyo", "Biologiya", "Tarix", "Ingliz tili", "Adabiyot", "Informatika", "Geografiya", "Ona tili"],
    "ru": ["Математика", "Физика", "Химия", "Биология", "История", "Английский", "Литература", "Информатика", "География", "Родной язык"],
    "en": ["Mathematics", "Physics", "Chemistry", "Biology", "History", "English", "Literature", "Informatics", "Geography", "Native Language"],
}

def get_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    return user

def get_tanlangan(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT fan FROM sevimli_fanlar WHERE user_id = ?", (user_id,))
    tanlangan = [r["fan"] for r in cur.fetchall()]
    db.close()
    return tanlangan

def sevimli_fan_keyboard(lang, tanlangan):
    fanlar = FANLAR.get(lang, FANLAR["uz"])
    buttons = []
    row = []
    for fan in fanlar:
        belgi = "✅ " if fan in tanlangan else ""
        row.append(InlineKeyboardButton(
            text=f"{belgi}{fan}",
            callback_data=f"sfan_{fan}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="💾 Saqlash", callback_data="sfan_saqlash")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(F.text.in_([
    TEXTS["uz"]["sevimli"], TEXTS["ru"]["sevimli"], TEXTS["en"]["sevimli"]
]))
async def sevimli_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    tanlangan = get_tanlangan(message.from_user.id)
    await state.set_state(SevimliState.tanlash)
    await state.update_data(tanlangan=tanlangan)
    await message.answer(
        "📌 Sevimli fanlaringizni tanlang:" if lang == "uz" else "📌 Выберите любимые предметы:" if lang == "ru" else "📌 Choose your favorite subjects:",
        reply_markup=bekor_keyboard(lang)
    )
    await message.answer(
        "👇 Fanni bosing (✅ tanlangan):" if lang == "uz" else "👇 Нажмите (✅ выбрано):" if lang == "ru" else "👇 Tap (✅ selected):",
        reply_markup=sevimli_fan_keyboard(lang, tanlangan)
    )

@router.callback_query(F.data.startswith("sfan_"))
async def sfan_tanlash(call: CallbackQuery, state: FSMContext):
    fan = call.data.split("_", 1)[1]
    user = get_user(call.from_user.id)
    lang = user["lang"] if user else "uz"

    if fan == "saqlash":
        data = await state.get_data()
        tanlangan = data.get("tanlangan", get_tanlangan(call.from_user.id))
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM sevimli_fanlar WHERE user_id = ?", (call.from_user.id,))
        for f in tanlangan:
            cur.execute("INSERT INTO sevimli_fanlar (user_id, fan) VALUES (?, ?)", (call.from_user.id, f))
        db.commit()
        db.close()
        await state.clear()
        await call.message.edit_text(
            f"✅ Saqlandi!\n\n📌 Sevimli fanlar: {', '.join(tanlangan) if tanlangan else 'Tanlanmagan'}" if lang == "uz"
            else f"✅ Сохранено!\n\n📌 Любимые предметы: {', '.join(tanlangan) if tanlangan else 'Не выбрано'}" if lang == "ru"
            else f"✅ Saved!\n\n📌 Favorite subjects: {', '.join(tanlangan) if tanlangan else 'None selected'}"
        )
        await call.message.answer("📋 Menyu:", reply_markup=main_keyboard(lang))
        return

    data = await state.get_data()
    tanlangan = list(data.get("tanlangan", get_tanlangan(call.from_user.id)))
    if fan in tanlangan:
        tanlangan.remove(fan)
    else:
        tanlangan.append(fan)
    await state.update_data(tanlangan=tanlangan)
    try:
        await call.message.edit_reply_markup(reply_markup=sevimli_fan_keyboard(lang, tanlangan))
    except:
        pass
