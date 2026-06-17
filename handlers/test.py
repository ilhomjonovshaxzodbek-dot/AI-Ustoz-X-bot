from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline_kb import fan_keyboard
from keyboards.main_kb import main_keyboard, bekor_keyboard, TEXTS
from database import get_db
from utils.gemini import test_ber, groq_request

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
        "👇 Fanni tanlang:" if lang == "uz" else "👇 Выберите предмет:" if lang == "ru" else "👇 Choose:",
        reply_markup=fan_keyboard(lang)
    )

@router.message(F.text.in_(["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]), TestState.fan_tanlash)
async def test_bekor_fan(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    await state.clear()
    await message.answer(
        "❌ Bekor qilindi." if lang == "uz" else "❌ Отменено." if lang == "ru" else "❌ Cancelled.",
        reply_markup=main_keyboard(lang)
    )

@router.message(F.text.in_(["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]), TestState.javob_kutish)
async def test_bekor_javob(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    await state.clear()
    await message.answer(
        "❌ Bekor qilindi." if lang == "uz" else "❌ Отменено." if lang == "ru" else "❌ Cancelled.",
        reply_markup=main_keyboard(lang)
    )

@router.callback_query(F.data.startswith("fan_"), TestState.fan_tanlash)
async def test_fan_handler(call: CallbackQuery, state: FSMContext):
    fan = call.data.split("_", 1)[1]
    user = get_user(call.from_user.id)
    lang = user["lang"]
    sinf = user["sinf"]
    
    await call.message.edit_text(
        "⏳ Test tayyorlanmoqda..." if lang == "uz" else "⏳ Готовлю тест..." if lang == "ru" else "⏳ Preparing..."
    )
    
    test = await test_ber(sinf, fan, lang)
    if not test:
        await call.message.edit_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
        await state.clear()
        return
    
    await state.update_data(
        fan=fan,
        sinf=sinf,
        lang=lang,
        savol_raqam=1,
        togri_soni=0,
        notogri_soni=0,
        jami=31
    )
    await state.set_state(TestState.javob_kutish)
    
    text = (
        f"🎯 *{fan}* | {sinf} | 1/31\n\n"
        f"{test['savol']}\n\n"
        f"A) {test['A']}\n"
        f"B) {test['B']}\n"
        f"C) {test['C']}\n"
        f"D) {test['D']}"
    )
    await state.update_data(joriy_test=test)
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=test_keyboard())

@router.callback_query(F.data.startswith("test_"), TestState.javob_kutish)
async def test_javob_handler(call: CallbackQuery, state: FSMContext):
    javob = call.data.split("_")[1]
    data = await state.get_data()
    
    fan = data["fan"]
    sinf = data["sinf"]
    lang = data["lang"]
    savol_raqam = data["savol_raqam"]
    togri_soni = data["togri_soni"]
    notogri_soni = data["notogri_soni"]
    jami = data["jami"]
    test = data["joriy_test"]
    togri = test["togri"]
    
    togri_bool = 1 if javob == togri else 0
    
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO testlar (user_id, savol, togri) VALUES (?, ?, ?)",
        (call.from_user.id, test["savol"], togri_bool)
    )
    db.commit()
    db.close()
    
    if togri_bool:
        togri_soni += 1
        natija_text = f"✅ To'g'ri! ({togri_soni}/{savol_raqam})" if lang == "uz" else f"✅ Правильно! ({togri_soni}/{savol_raqam})" if lang == "ru" else f"✅ Correct! ({togri_soni}/{savol_raqam})"
    else:
        notogri_soni += 1
        natija_text = (
            f"❌ Noto'g'ri! To'g'ri javob: *{togri}* ({togri_soni}/{savol_raqam})" if lang == "uz"
            else f"❌ Неправильно! Правильный ответ: *{togri}* ({togri_soni}/{savol_raqam})" if lang == "ru"
            else f"❌ Wrong! Correct answer: *{togri}* ({togri_soni}/{savol_raqam})"
        )
    
    await call.message.edit_text(natija_text, parse_mode="Markdown")
    
    if savol_raqam >= jami:
        ball = round((togri_soni / jami) * 100)
        
        if ball == 100:
            prompt = f"O'quvchi testda 100 ball oldi! {fan} fanidan. 100 ta harfdan iborat qisqa motivatsiyali tabrik yoz o'zbek tilida. Har safar boshqacha bo'lsin."
            motivatsiya = await groq_request(prompt)
            
            user = get_user(call.from_user.id)
            db2 = get_db()
            cur2 = db2.cursor()
            cur2.execute("SELECT tg_id FROM users")
            barcha = cur2.fetchall()
            db2.close()
            
            for u in barcha:
                try:
                    await call.bot.send_message(
                        u["tg_id"],
                        f"🏆 *{user['name']}* {fan} fanidan *100 ball* oldi!\n\n{motivatsiya}",
                        parse_mode="Markdown"
                    )
                except:
                    pass
        
        if ball >= 90:
            baho = "A'lo ⭐⭐⭐⭐⭐"
        elif ball >= 70:
            baho = "Yaxshi ⭐⭐⭐⭐"
        elif ball >= 50:
            baho = "Qoniqarli ⭐⭐⭐"
        else:
            baho = "Qoniqarsiz ⭐⭐"
        
        yakuniy = (
            f"🏁 *Test yakunlandi!*\n\n"
            f"📚 Fan: *{fan}*\n"
            f"✅ To'g'ri: *{togri_soni}*\n"
            f"❌ Noto'g'ri: *{notogri_soni}*\n"
            f"📊 Ball: *{ball}/100*\n"
            f"🎓 Baho: *{baho}*"
        )
        
        await state.clear()
        await call.message.answer(yakuniy, parse_mode="Markdown", reply_markup=main_keyboard(lang))
        
        from handlers.yutuqlar import yutuq_tekshir
        await yutuq_tekshir(call.bot, call.from_user.id)
        return
    
    await state.update_data(
        savol_raqam=savol_raqam + 1,
        togri_soni=togri_soni,
        notogri_soni=notogri_soni
    )
    
    yangi_test = await test_ber(sinf, fan, lang)
    if not yangi_test:
        await call.message.answer("❌ Xatolik! Qayta urinib ko'ring.")
        await state.clear()
        return
    
    await state.update_data(joriy_test=yangi_test)
    
    text = (
        f"🎯 *{fan}* | {sinf} | {savol_raqam + 1}/31\n\n"
        f"{yangi_test['savol']}\n\n"
        f"A) {yangi_test['A']}\n"
        f"B) {yangi_test['B']}\n"
        f"C) {yangi_test['C']}\n"
        f"D) {yangi_test['D']}"
    )
    await call.message.answer(text, parse_mode="Markdown", reply_markup=test_keyboard())
