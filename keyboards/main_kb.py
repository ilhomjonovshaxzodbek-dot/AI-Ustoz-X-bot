from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TEXTS = {
    "uz": {
        "masala": "📚 Masala ol",
        "savol": "❓ Savol ber",
        "tushuntir": "📖 Tushuntir",
        "test": "🎯 Test ishlash",
        "insho": "📝 Insho/Matn",
        "eslatma": "🔔 Eslatma",
        "natija": "📊 Natijalarim",
        "reyting": "🏆 Reyting",
        "sozlama": "⚙️ Sozlamalar",
    },
    "ru": {
        "masala": "📚 Получить задачу",
        "savol": "❓ Задать вопрос",
        "tushuntir": "📖 Объяснить",
        "test": "🎯 Пройти тест",
        "insho": "📝 Сочинение",
        "eslatma": "🔔 Напоминание",
        "natija": "📊 Мои результаты",
        "reyting": "🏆 Рейтинг",
        "sozlama": "⚙️ Настройки",
    },
    "en": {
        "masala": "📚 Get Task",
        "savol": "❓ Ask Question",
        "tushuntir": "📖 Explain",
        "test": "🎯 Take Test",
        "insho": "📝 Essay",
        "eslatma": "🔔 Reminder",
        "natija": "📊 My Results",
        "reyting": "🏆 Ranking",
        "sozlama": "⚙️ Settings",
    }
}

def main_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    t = TEXTS.get(lang, TEXTS["uz"])
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["masala"]), KeyboardButton(text=t["savol"])],
            [KeyboardButton(text=t["tushuntir"]), KeyboardButton(text=t["test"])],
            [KeyboardButton(text=t["insho"]), KeyboardButton(text=t["eslatma"])],
            [KeyboardButton(text=t["natija"]), KeyboardButton(text=t["reyting"])],
            [KeyboardButton(text=t["sozlama"])],
        ],
        resize_keyboard=True
    )

def sozlamalar_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    if lang == "uz":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🌐 Tilni o'zgartirish")],
                [KeyboardButton(text="🎓 Sinf/Kursni o'zgartirish")],
                [KeyboardButton(text="🔙 Orqaga")],
            ],
            resize_keyboard=True
        )
    elif lang == "ru":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🌐 Сменить язык")],
                [KeyboardButton(text="🎓 Сменить класс/курс")],
                [KeyboardButton(text="🔙 Назад")],
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🌐 Change Language")],
                [KeyboardButton(text="🎓 Change Class/Course")],
                [KeyboardButton(text="🔙 Back")],
            ],
            resize_keyboard=True
        )
