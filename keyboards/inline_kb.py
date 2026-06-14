from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNELS

def sub_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"📢 Kanal {i+1}", url=f"https://t.me/{ch.lstrip('@')}")] 
        for i, ch in enumerate(CHANNELS)
    ]
    buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    ])

def sinf_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i in range(1, 12):
        row.append(InlineKeyboardButton(text=f"{i}-sinf", callback_data=f"sinf_{i}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🎓 Talaba", callback_data="sinf_talaba")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def kurs_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1-kurs", callback_data="kurs_1"),
            InlineKeyboardButton(text="2-kurs", callback_data="kurs_2"),
        ],
        [
            InlineKeyboardButton(text="3-kurs", callback_data="kurs_3"),
            InlineKeyboardButton(text="4-kurs", callback_data="kurs_4"),
        ],
    ])

def fan_keyboard(lang: str) -> InlineKeyboardMarkup:
    fanlar = {
        "uz": ["Matematika", "Fizika", "Kimyo", "Biologiya", "Tarix", "Ingliz tili", "Adabiyot", "Informatika"],
        "ru": ["Математика", "Физика", "Химия", "Биология", "История", "Английский", "Литература", "Информатика"],
        "en": ["Mathematics", "Physics", "Chemistry", "Biology", "History", "English", "Literature", "Informatics"],
    }
    buttons = []
    row = []
    for fan in fanlar.get(lang, fanlar["uz"]):
        row.append(InlineKeyboardButton(text=fan, callback_data=f"fan_{fan}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)
