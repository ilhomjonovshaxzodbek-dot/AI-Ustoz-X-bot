from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.bot import Bot
from config import CHANNELS
from typing import Callable, Dict, Any

async def check_subscription(bot: Bot, user_id: int) -> bool:
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked", "banned"]:
                return False
        except:
            return False
    return True

class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        bot = data["bot"]
        
        if isinstance(event, Message):
            user_id = event.from_user.id
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            if event.data == "check_sub":
                subscribed = await check_subscription(bot, user_id)
                if subscribed:
                    await event.answer("✅ Obuna tasdiqlandi!")
                    from handlers.start import send_lang_menu
                    await send_lang_menu(event.message, user_id)
                else:
                    await event.answer("❌ Hali obuna bo'lmadingiz!", show_alert=True)
                return
        else:
            return await handler(event, data)

        subscribed = await check_subscription(bot, user_id)
        if not subscribed:
            from keyboards.inline_kb import sub_keyboard
            if isinstance(event, Message):
                await event.answer(
                    "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
                    reply_markup=sub_keyboard()
                )
            return
        
        return await handler(event, data)
