from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.main_kb import main_keyboard, TEXTS
from database import get_db

router = Router()

class EslatmaState(StatesGroup):
    vaqt_kutish = State()

def get_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    return user

@router.message(F.text.in_([
    TEXTS["uz"]["eslatma"], TEXTS["ru"]["eslatma"], TEXTS["en"]["eslatma"]
]))
async def eslatma_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["lang"]
    
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT vaqt, active FROM eslatmalar WHERE user_id = ?", (message.from_user.id,))
    eslatma = cur.fetchone()
    db.close()
    
    if eslatma and eslatma["active"]:
        await message.answer(
            f"🔔 Eslatma {eslatma['vaqt']} da o'rnatilgan.\n\nO'zgartirish uchun yangi vaqt yozing (HH:MM):" if lang == "uz"
            else f"🔔 Напоминание установлено на {eslatma['vaqt']}.\n\nДля изменения напишите новое время (HH:MM):" if lang == "ru"
            else f"🔔 Reminder set at {eslatma['vaqt']}.\n\nTo change, write new time (HH:MM):"
        )
    else:
        await message.answer(
            "🔔 Kunlik eslatma vaqtini kiriting (HH:MM formatda, masalan: 08:00):" if lang == "uz"
            else "🔔 Введите время ежедневного напоминания (формат HH:MM, например: 08:00):" if lang == "ru"
            else "🔔 Enter daily reminder time (HH:MM format, e.g. 08:00):"
        )
    await state.set_state(EslatmaState.vaqt_kutish)

@router.message(EslatmaState.vaqt_kutish)
async def vaqt_handler(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["lang"]
    vaqt = message.text.strip()
    
    import re
    if not re.match(r"^\d{2}:\d{2}$", vaqt):
        await message.answer(
            "❌ Noto'g'ri format! HH:MM formatda yozing (masalan: 08:00)" if lang == "uz"
            else "❌ Неверный формат! Введите в формате HH:MM (например: 08:00)" if lang == "ru"
            else "❌ Wrong format! Write in HH:MM format (e.g. 08:00)"
        )
        return
    
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO eslatmalar (user_id, vaqt, active) VALUES (?, ?, 1)",
        (message.from_user.id, vaqt)
    )
    db.commit()
    db.close()
    
    await state.clear()
    await message.answer(
        f"✅ Eslatma {vaqt} ga o'rnatildi!" if lang == "uz"
        else f"✅ Напоминание установлено на {vaqt}!" if lang == "ru"
        else f"✅ Reminder set for {vaqt}!",
        reply_markup=main_keyboard(lang)
    )
