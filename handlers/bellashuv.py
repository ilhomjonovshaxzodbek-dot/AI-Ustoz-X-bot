from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline_kb import fan_keyboard
from keyboards.main_kb import main_keyboard, TEXTS
from database import get_db
from utils.gemini import groq_request

router = Router()

class BellashuvState(StatesGroup):
    fan_tanlash = State()
    raqib_tanlash = State()
    savol_soni = State()
    javob_kutish = State()

def get_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    return user

def raqib_keyboard(users, current_user_id):
    buttons = []
    for u in users:
        if u["tg_id"] != current_user_id:
            buttons.append([InlineKeyboardButton(
                text=f"👤 {u['name']}",
                callback_data=f"raqib_{u['tg_id']}"
            )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def raqib_taklif_keyboard(bellashuv_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Qabul qilaman", callback_data=f"qabul_{bellashuv_id}")],
        [InlineKeyboardButton(text="❌ Yo'q", callback_data=f"rad_{bellashuv_id}")],
    ])

def boshlash_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Bot tanlaydi", callback_data="raqib_bot")],
        [InlineKeyboardButton(text="👤 O'zim tanlaymen", callback_data="raqib_ozim")],
    ])

@router.message(F.text.in_([
    TEXTS["uz"]["bellashuv"], TEXTS["ru"]["bellashuv"], TEXTS["en"]["bellashuv"]
]))
async def bellashuv_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user or not user["sinf"]:
        await message.answer("⚠️ Avval sinf/kursni tanlang!")
        return
    lang = user["lang"]
    await state.set_state(BellashuvState.fan_tanlash)
    await message.answer(
        "⚔️ Qaysi fandan bellashasiz?" if lang == "uz" else "⚔️ По какому предмету?" if lang == "ru" else "⚔️ Which subject?",
        reply_markup=fan_keyboard(lang)
    )

@router.callback_query(F.data.startswith("fan_"), BellashuvState.fan_tanlash)
async def fan_tanlash_handler(call: CallbackQuery, state: FSMContext):
    fan = call.data.split("_", 1)[1]
    user = get_user(call.from_user.id)
    lang = user["lang"]
    await state.update_data(fan=fan)
    await state.set_state(BellashuvState.raqib_tanlash)
    await call.message.edit_text(
        f"⚔️ *{fan}* fani tanlandi!\n\nRaqibni qanday tanlaysiz?" if lang == "uz"
        else f"⚔️ Предмет *{fan}* выбран!\n\nКак выбрать соперника?" if lang == "ru"
        else f"⚔️ Subject *{fan}* selected!\n\nHow to choose opponent?",
        parse_mode="Markdown",
        reply_markup=boshlash_keyboard()
    )

@router.callback_query(F.data == "raqib_bot", BellashuvState.raqib_tanlash)
async def raqib_bot_handler(call: CallbackQuery, state: FSMContext):
    user = get_user(call.from_user.id)
    lang = user["lang"]
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id != ? ORDER BY RANDOM() LIMIT 1", (call.from_user.id,))
    raqib = cur.fetchone()
    db.close()
    
    if not raqib:
        await call.message.edit_text("❌ Hozircha boshqa o'quvchi yo'q!")
        await state.clear()
        return
    
    await state.update_data(raqib_id=raqib["tg_id"], raqib_name=raqib["name"])
    data = await state.get_data()
    
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO bellashuv (boshlagan, raqib, fan, holat) VALUES (?, ?, ?, 'kutish')",
        (call.from_user.id, raqib["tg_id"], data["fan"])
    )
    bellashuv_id = cur.lastrowid
    db.commit()
    db.close()
    
    await state.update_data(bellashuv_id=bellashuv_id)
    
    bot = call.bot
    await bot.send_message(
        raqib["tg_id"],
        f"⚔️ *{user['name']}* siz bilan *{data['fan']}* fanidan bellashishni xohlayapti!\n\nQabul qilasizmi?",
        parse_mode="Markdown",
        reply_markup=raqib_taklif_keyboard(bellashuv_id)
    )
    
    await call.message.edit_text(
        f"✅ *{raqib['name']}* ga taklif yuborildi. Javob kutilmoqda..." if lang == "uz"
        else f"✅ Приглашение отправлено *{raqib['name']}*. Ожидание ответа..." if lang == "ru"
        else f"✅ Invitation sent to *{raqib['name']}*. Waiting for response...",
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "raqib_ozim", BellashuvState.raqib_tanlash)
async def raqib_ozim_handler(call: CallbackQuery, state: FSMContext):
    user = get_user(call.from_user.id)
    lang = user["lang"]
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id != ?", (call.from_user.id,))
    users = cur.fetchall()
    db.close()
    
    if not users:
        await call.message.edit_text("❌ Hozircha boshqa o'quvchi yo'q!")
        await state.clear()
        return
    
    await call.message.edit_text(
        "👤 Raqibni tanlang:" if lang == "uz" else "👤 Выберите соперника:" if lang == "ru" else "👤 Choose opponent:",
        reply_markup=raqib_keyboard(users, call.from_user.id)
    )

@router.callback_query(F.data.startswith("raqib_") & ~F.data.in_(["raqib_bot", "raqib_ozim"]), BellashuvState.raqib_tanlash)
async def raqib_tanlandi_handler(call: CallbackQuery, state: FSMContext):
    raqib_id = int(call.data.split("_")[1])
    user = get_user(call.from_user.id)
    raqib = get_user(raqib_id)
    lang = user["lang"]
    data = await state.get_data()
    
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO bellashuv (boshlagan, raqib, fan, holat) VALUES (?, ?, ?, 'kutish')",
        (call.from_user.id, raqib_id, data["fan"])
    )
    bellashuv_id = cur.lastrowid
    db.commit()
    db.close()
    
    await state.update_data(raqib_id=raqib_id, raqib_name=raqib["name"], bellashuv_id=bellashuv_id)
    
    bot = call.bot
    await bot.send_message(
        raqib_id,
        f"⚔️ *{user['name']}* siz bilan *{data['fan']}* fanidan bellashishni xohlayapti!\n\nQabul qilasizmi?",
        parse_mode="Markdown",
        reply_markup=raqib_taklif_keyboard(bellashuv_id)
    )
    
    await call.message.edit_text(
        f"✅ *{raqib['name']}* ga taklif yuborildi. Javob kutilmoqda..." if lang == "uz"
        else f"✅ Приглашение отправлено *{raqib['name']}*. Ожидание ответа..." if lang == "ru"
        else f"✅ Invitation sent to *{raqib['name']}*. Waiting for response...",
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("qabul_"))
async def qabul_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    bellashuv_id = int(call.data.split("_")[1])
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM bellashuv WHERE id = ?", (bellashuv_id,))
    b = cur.fetchone()
    
    if not b:
        await call.answer("❌ Bellashuv topilmadi!")
        db.close()
        return
    
    boshlagan = get_user(b["boshlagan"])
    lang = boshlagan["lang"]
    
    await bot.send_message(
        b["boshlagan"],
        f"✅ *{call.from_user.full_name}* bellashuvni qabul qildi!\n\n"
        f"Nechta savol bo'lsin? (5 tadan kam bo'lmasin)",
        parse_mode="Markdown"
    )
    
    await call.message.edit_text(
        f"✅ Qabul qildingiz! Bellashuv boshlanmoqda, kuting..." if b["raqib"] == call.from_user.id
        else "✅ Принято! Ожидайте начала..."
    )
    
    cur.execute("UPDATE bellashuv SET holat = 'savol_kutish' WHERE id = ?", (bellashuv_id,))
    db.commit()
    db.close()
    
    await state.set_state(BellashuvState.savol_soni)
    await state.update_data(bellashuv_id=bellashuv_id)

@router.callback_query(F.data.startswith("rad_"))
async def rad_handler(call: CallbackQuery, bot: Bot):
    bellashuv_id = int(call.data.split("_")[1])
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM bellashuv WHERE id = ?", (bellashuv_id,))
    b = cur.fetchone()
    
    if b:
        await bot.send_message(
            b["boshlagan"],
            f"❌ *{call.from_user.full_name}* bellashuvni rad etdi.",
            parse_mode="Markdown"
        )
        cur.execute("DELETE FROM bellashuv WHERE id = ?", (bellashuv_id,))
        db.commit()
    db.close()
    
    await call.message.edit_text("❌ Bellashuvni rad etdingiz.")

@router.message(BellashuvState.savol_soni)
async def savol_soni_handler(message: Message, state: FSMContext, bot: Bot):
    user = get_user(message.from_user.id)
    lang = user["lang"]
    
    try:
        soni = int(message.text.strip())
        if soni < 5:
            await message.answer("⚠️ Kamida 5 ta savol bo'lishi kerak!" if lang == "uz" else "⚠️ Минимум 5 вопросов!" if lang == "ru" else "⚠️ Minimum 5 questions!")
            return
    except:
        await message.answer("⚠️ Faqat raqam yozing!" if lang == "uz" else "⚠️ Введите число!" if lang == "ru" else "⚠️ Enter a number!")
        return
    
    data = await state.get_data()
    bellashuv_id = data["bellashuv_id"]
    
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE bellashuv SET savol_soni = ?, holat = 'jarayonda' WHERE id = ?", (soni, bellashuv_id))
    cur.execute("SELECT * FROM bellashuv WHERE id = ?", (bellashuv_id,))
    b = cur.fetchone()
    db.commit()
    db.close()
    
    raqib = get_user(b["raqib"])
    
    await bot.send_message(
        b["raqib"],
        f"⚔️ Bellashuv boshlandi! *{soni}* ta savol bo'ladi.\n\n1-savol tayyorlanmoqda...",
        parse_mode="Markdown"
    )
    
    await message.answer(
        f"⚔️ Bellashuv boshlandi! *{soni}* ta savol bo'ladi.\n\n1-savol tayyorlanmoqda...",
        parse_mode="Markdown"
    )
    
    await state.clear()
    await yuborish_savol(bot, bellashuv_id, b["boshlagan"], b["raqib"], b["fan"], soni)

async def yuborish_savol(bot: Bot, bellashuv_id: int, boshlagan_id: int, raqib_id: int, fan: str, savol_soni: int):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM bellashuv WHERE id = ?", (bellashuv_id,))
    b = cur.fetchone()
    db.close()
    
    boshlagan_user = get_user(boshlagan_id)
    raqib_user = get_user(raqib_id)
    
    for user_id, user_data in [(boshlagan_id, boshlagan_user), (raqib_id, raqib_user)]:
        lang = user_data["lang"]
        til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
        prompt = f"Sen AI ustoz botsan. {user_data['sinf']} uchun {fan} fanidan bitta masala/misol ber {til}. Faqat masalani yoz, javobini yozma."
        savol = await groq_request(prompt)
        
        db = get_db()
        cur = db.cursor()
        if user_id == boshlagan_id:
            cur.execute("UPDATE bellashuv SET boshlagan_savol = boshlagan_savol + 0 WHERE id = ?", (bellashuv_id,))
        db.commit()
        db.close()
        
        await bot.send_message(
            user_id,
            f"⚔️ *Bellashuv* | {fan}\n\n📝 Savol:\n{savol}\n\nJavobingizni yozing:",
            parse_mode="Markdown"
        )
