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

def savol_soni_keyboard(bellashuv_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="5️⃣ 5 ta", callback_data=f"bsoni_{bellashuv_id}_5")],
        [InlineKeyboardButton(text="7️⃣ 7 ta", callback_data=f"bsoni_{bellashuv_id}_7")],
        [InlineKeyboardButton(text="🔟 10 ta", callback_data=f"bsoni_{bellashuv_id}_10")],
        [InlineKeyboardButton(text="✏️ O'zim kiritaman", callback_data=f"bsoni_{bellashuv_id}_0")],
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
        f"⚔️ *{fan}* fani tanlandi!\n\nRaqibni qanday tanlaysiz?",
        parse_mode="Markdown",
        reply_markup=boshlash_keyboard()
    )

@router.callback_query(F.data == "raqib_bot", BellashuvState.raqib_tanlash)
async def raqib_bot_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
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
    
    await state.clear()
    
    await bot.send_message(
        raqib["tg_id"],
        f"⚔️ *{user['name']}* siz bilan *{data['fan']}* fanidan bellashishni xohlayapti!\n\nQabul qilasizmi?",
        parse_mode="Markdown",
        reply_markup=raqib_taklif_keyboard(bellashuv_id)
    )
    
    await call.message.edit_text(
        f"✅ *{raqib['name']}* ga taklif yuborildi. Javob kutilmoqda...",
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "raqib_ozim", BellashuvState.raqib_tanlash)
async def raqib_ozim_handler(call: CallbackQuery, state: FSMContext):
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
        "👤 Raqibni tanlang:",
        reply_markup=raqib_keyboard(users, call.from_user.id)
    )

@router.callback_query(F.data.startswith("raqib_"), BellashuvState.raqib_tanlash)
async def raqib_tanlandi_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    if call.data in ["raqib_bot", "raqib_ozim"]:
        return
    
    raqib_id = int(call.data.split("_")[1])
    user = get_user(call.from_user.id)
    raqib = get_user(raqib_id)
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
    
    await state.clear()
    
    await bot.send_message(
        raqib_id,
        f"⚔️ *{user['name']}* siz bilan *{data['fan']}* fanidan bellashishni xohlayapti!\n\nQabul qilasizmi?",
        parse_mode="Markdown",
        reply_markup=raqib_taklif_keyboard(bellashuv_id)
    )
    
    await call.message.edit_text(
        f"✅ *{raqib['name']}* ga taklif yuborildi. Javob kutilmoqda...",
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("qabul_"))
async def qabul_handler(call: CallbackQuery, bot: Bot):
    bellashuv_id = int(call.data.split("_")[1])
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM bellashuv WHERE id = ?", (bellashuv_id,))
    b = cur.fetchone()
    
    if not b:
        await call.answer("❌ Bellashuv topilmadi!")
        db.close()
        return
    
    cur.execute("UPDATE bellashuv SET holat = 'savol_kutish' WHERE id = ?", (bellashuv_id,))
    db.commit()
    db.close()
    
    await call.message.edit_text("✅ Qabul qildingiz! Bellashuv boshlanmoqda, kuting...")
    
    await bot.send_message(
        b["boshlagan"],
        f"✅ *{call.from_user.full_name}* bellashuvni qabul qildi!\n\nNechta savol bo'lsin?",
        parse_mode="Markdown",
        reply_markup=savol_soni_keyboard(bellashuv_id)
    )

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

@router.callback_query(F.data.startswith("bsoni_"))
async def bsoni_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    parts = call.data.split("_")
    bellashuv_id = int(parts[1])
    soni = int(parts[2])
    
    if soni == 0:
        await state.set_state(BellashuvState.savol_soni)
        await state.update_data(bellashuv_id=bellashuv_id)
        await call.message.edit_text("✏️ Savol sonini yozing (5 tadan kam bo'lmasin):")
        return
    
    await call.message.edit_text(f"✅ {soni} ta savol tanlandi! Bellashuv boshlanmoqda...")
    await boshlash_bellashuv(bot, bellashuv_id, soni)

@router.message(BellashuvState.savol_soni)
async def savol_soni_handler(message: Message, state: FSMContext, bot: Bot):
    try:
        soni = int(message.text.strip())
        if soni < 5:
            await message.answer("⚠️ Kamida 5 ta savol bo'lishi kerak!")
            return
    except:
        await message.answer("⚠️ Faqat raqam yozing!")
        return
    
    data = await state.get_data()
    bellashuv_id = data["bellashuv_id"]
    await state.clear()
    await message.answer(f"✅ {soni} ta savol! Bellashuv boshlanmoqda...")
    await boshlash_bellashuv(bot, bellashuv_id, soni)

async def boshlash_bellashuv(bot: Bot, bellashuv_id: int, soni: int):
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE bellashuv SET savol_soni = ?, holat = 'jarayonda' WHERE id = ?", (soni, bellashuv_id))
    cur.execute("SELECT * FROM bellashuv WHERE id = ?", (bellashuv_id,))
    b = cur.fetchone()
    db.commit()
    db.close()
    
    xabar = f"⚔️ *Bellashuv boshlandi!*\n\n📚 Fan: *{b['fan']}*\n❓ Savollar: *{soni}* ta\n\n1-savol tayyorlanmoqda..."
    
    await bot.send_message(b["boshlagan"], xabar, parse_mode="Markdown")
    await bot.send_message(b["raqib"], xabar, parse_mode="Markdown")
    
    await yuborish_savol(bot, bellashuv_id, b["boshlagan"], b["raqib"], b["fan"], soni, 1)

async def yuborish_savol(bot: Bot, bellashuv_id: int, boshlagan_id: int, raqib_id: int, fan: str, savol_soni: int, savol_raqam: int):
    boshlagan = get_user(boshlagan_id)
    raqib = get_user(raqib_id)
    
    for user_id, user_data in [(boshlagan_id, boshlagan), (raqib_id, raqib)]:
        lang = user_data["lang"]
        sinf = user_data["sinf"] or "10-sinf"
        til = {"uz": "o'zbek tilida", "ru": "на русском языке", "en": "in English"}.get(lang, "o'zbek tilida")
        
        prompt = f"Sen AI ustoz botsan. {sinf} uchun {fan} fanidan bitta masala/misol ber {til}. Faqat masalani yoz, javobini yozma. Masala qisqa va tushunarli bo'lsin."
        savol = await groq_request(prompt)
        
        db = get_db()
        cur = db.cursor()
        if user_id == boshlagan_id:
            cur.execute("UPDATE bellashuv SET boshlagan_savol = ? WHERE id = ?", (savol_raqam, bellashuv_id))
        else:
            cur.execute("UPDATE bellashuv SET raqib_savol = ? WHERE id = ?", (savol_raqam, bellashuv_id))
        db.commit()
        db.close()
        
        await bot.send_message(
            user_id,
            f"⚔️ *Bellashuv* | {fan} | {savol_raqam}/{savol_soni}\n\n📝 {savol}\n\nJavobingizni yozing:",
            parse_mode="Markdown"
        )
