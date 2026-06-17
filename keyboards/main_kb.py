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
        "yordam": "🆘 Yordam",
        "bellashuv": "⚔️ Bilim bellashuvi",
        "yutuqlar": "🏅 Yutuqlar",
        "haftalik": "📈 Haftalik hisobot",
        "sevimli": "📌 Sevimli fanlar",
        "bekor": "❌ Bekor qilish",
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
        "yordam": "🆘 Помощь",
        "bellashuv": "⚔️ Битва знаний",
        "yutuqlar": "🏅 Достижения",
        "haftalik": "📈 Недельный отчёт",
        "sevimli": "📌 Любимые предметы",
        "bekor": "❌ Отмена",
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
        "yordam": "🆘 Help",
        "bellashuv": "⚔️ Knowledge Battle",
        "yutuqlar": "🏅 Achievements",
        "haftalik": "📈 Weekly Report",
        "sevimli": "📌 Favorite Subjects",
        "bekor": "❌ Cancel",
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
            [KeyboardButton(text=t["bellashuv"]), KeyboardButton(text=t["yutuqlar"])],
            [KeyboardButton(text=t["haftalik"]), KeyboardButton(text=t["sevimli"])],
            [KeyboardButton(text=t["sozlama"]), KeyboardButton(text=t["yordam"])],
        ],
        resize_keyboard=True
    )

def bekor_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    t = TEXTS.get(lang, TEXTS["uz"])
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["bekor"])],
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
