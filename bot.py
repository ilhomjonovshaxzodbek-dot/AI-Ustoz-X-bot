import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import create_tables
from middlewares.subscription import SubscriptionMiddleware
from handlers import start, masala, savol, tushuntir, test, insho, eslatma, natijalar, reyting, sozlamalar

logging.basicConfig(level=logging.INFO)

async def send_eslatmalar(bot: Bot):
    from database import get_db
    import datetime
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT user_id FROM eslatmalar WHERE vaqt = ? AND active = 1", (now,))
        users = cur.fetchall()
        db.close()
        for u in users:
            try:
                await bot.send_message(
                    u["user_id"],
                    "📚 O'qish vaqti! Bugun ham o'rganishni davom ettiring! 💪"
                )
            except:
                pass
        await asyncio.sleep(60)

async def main():
    create_tables()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())
    
    dp.include_router(start.router)
    dp.include_router(masala.router)
    dp.include_router(savol.router)
    dp.include_router(tushuntir.router)
    dp.include_router(test.router)
    dp.include_router(insho.router)
    dp.include_router(eslatma.router)
    dp.include_router(natijalar.router)
    dp.include_router(reyting.router)
    dp.include_router(sozlamalar.router)
    
    asyncio.create_task(send_eslatmalar(bot))
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
