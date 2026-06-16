from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

CHANNELS = [
    "@shzodbekcoderdev",
    "@faylmasteruzbot", 
    "@hisobchixuzbot"
]

LANGUAGES = {
    "uz": "🇺🇿 O'zbek",
    "ru": "🇷🇺 Rus",
    "en": "🇬🇧 Ingliz"
}
