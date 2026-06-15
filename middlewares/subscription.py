from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any

class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        return await handler(event, data)
