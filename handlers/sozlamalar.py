from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.main_kb import main_keyboard, sozlamalar_keyboard, TEXTS
from keyboards.inline_kb import lang_keyboard, sinf_keyboard
from database import get_db

router = Router()

def get_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (user_id,))
    user = cur.fetchone()
    db.close()
    return user

YORDAM_MATNI = {
    "uz": """❓ *Yordam — AI Ustoz X bot*

📚 *Masala ol* — Bot sizga fan bo'yicha masala beradi. Siz yechasiz, bot tekshirib tushuntiradi.

❓ *Savol ber* — Tushunmagan narsangizni yozing, AI tushuntiradi.

📖 *Tushuntir* — Mavzu nomini yozing, AI batafsil tushuntiradi.

🎯 *Test ishlash* — A/B/C/D variantli test ishlaysiz, bot natijani aytadi.

📝 *Insho/Matn* — Insho yozasiz, AI baho berib tavsiyalar beradi.

🔔 *Eslatma* — Kunlik o'qish uchun vaqt belgilaysiz.

📊 *Natijalarim* — Qancha masala va test ishlaganingiz ko'rsatiladi.

🏆 *Reyting* — Eng faol o'quvchilar ro'yxati.

⚙️ *Sozlamalar* — Tilni yoki sinf/kursni o'zgartirasiz.""",

    "ru": """❓ *Помощь — AI Ustoz X bot*

📚 *Получить задачу* — Бот даёт задачу по предмету. Вы решаете, бот проверяет и объясняет.

❓ *Задать вопрос* — Напишите что не понимаете, AI объяснит.

📖 *Объяснить* — Напишите тему, AI объяснит подробно.

🎯 *Пройти тест* — Тест с вариантами A/B/C/D, бот скажет результат.

📝 *Сочинение* — Пишете сочинение, AI оценивает и даёт советы.

🔔 *Напоминание* — Устанавливаете время для ежедневного чтения.

📊 *Мои результаты* — Показывает сколько задач и тестов выполнено.

🏆 *Рейтинг* — Список самых активных учеников.

⚙️ *Настройки* — Меняете язык или класс/курс.""",

    "en": """❓ *Help — AI Ustoz X bot*

📚 *Get Task* — Bot gives you a task by subject. You solve it, bot checks and explains.

❓ *Ask Question* — Write what you don't understand, AI explains.

📖 *Explain* — Write a topic name, AI explains in detail.

🎯 *Take Test* — A/B/C/D multiple choice test, bot tells the result.

📝 *Essay* — You write an essay, AI grades and gives advice.

🔔 *Reminder* — Set a time for daily reading.

📊 *My Results* — Shows how many tasks and tests completed.

🏆 *Ranking* — List of most active students.

⚙️ *Settings* — Change language or class/course."""
}

@router.message(F.text.in_([
    TEXTS["uz"]["sozlama"], TEXTS["ru"]["sozlama"], TEXTS["en"]["sozlama"]
]))
async def sozlamalar_handler(message: Message):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    await message.answer(
        "⚙️ Sozlamalar:" if lang == "uz" else "⚙️ Настройки:" if lang == "ru" else "⚙️ Settings:",
        reply_markup=sozlamalar_keyboard(lang)
    )

@router.message(F.text.in_([
    TEXTS["uz"]["yordam"], TEXTS["ru"]["yordam"], TEXTS["en"]["yordam"]
]))
async def yordam_handler(message: Message):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    await message.answer(
        YORDAM_MATNI[lang],
        parse_mode="Markdown",
        reply_markup=main_keyboard(lang)
    )

@router.message(F.text.in_(["🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Change Language"]))
async def til_ozgartir(message: Message):
    await message.answer(
        "🌐 Tilni tanlang:",
        reply_markup=lang_keyboard()
    )

@router.message(F.text.in_(["🎓 Sinf/Kursni o'zgartirish", "🎓 Сменить класс/курс", "🎓 Change Class/Course"]))
async def sinf_ozgartir(message: Message):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    await message.answer(
        "🎓 Sinfingizni tanlang:" if lang == "uz" else "🎓 Выберите класс:" if lang == "ru" else "🎓 Choose class:",
        reply_markup=sinf_keyboard()
    )

@router.message(F.text.in_(["🔙 Orqaga", "🔙 Назад", "🔙 Back"]))
async def orqaga(message: Message):
    user = get_user(message.from_user.id)
    lang = user["lang"] if user else "uz"
    await message.answer(
        "📋 Menyu:" if lang == "uz" else "📋 Меню:" if lang == "ru" else "📋 Menu:",
        reply_markup=main_keyboard(lang)
    )
