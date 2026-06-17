import asyncio
import logging
import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import create_tables
from middlewares.subscription import SubscriptionMiddleware
from handlers import start, masala, savol, tushuntir, test, insho, eslatma, natijalar, reyting, sozlamalar, bellashuv, yutuqlar, haftalik, sevimli

logging.basicConfig(level=logging.INFO)

MOTIVATSIYA = [
    "🌟 Har kuni o'rganish — muvaffaqiyat sari bir qadam!",
    "💪 Bilim — eng kuchli qurol!",
    "🚀 Bugun o'rgangan narsang ertangi kuning poydevori!",
    "🎯 Maqsadingga erishish uchun har kuni harakat qil!",
    "📚 Kitob o'qigan odam hech qachon yolg'iz emas!",
    "⭐ Sen qila olasan! Faqat harakat kerak!",
    "🔥 Zo'r natijalar zo'r harakatlardan kelib chiqadi!",
    "🌈 Har bir yangi bilim yangi imkoniyat ochadi!",
    "💡 Savol berish — bilimning boshlanishi!",
    "🏆 G'olib bo'lish uchun avval o'rganish kerak!",
]

async def motivatsiya_yuborish(bot: Bot):
    from database import get_db
    import random
    while True:
        now = datetime.datetime.now()
        if now.hour == 8 and now.minute == 0:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT tg_id, lang FROM users")
            users = cur.fetchall()
            db.close()
            
            gap = random.choice(MOTIVATSIYA)
            for u in users:
                try:
                    await bot.send_message(u["tg_id"], gap)
                except:
                    pass
        await asyncio.sleep(60)

async def haftalik_yuborish_task(bot: Bot):
    from handlers.haftalik import haftalik_yuborish
    while True:
        now = datetime.datetime.now()
        if now.weekday() == 0 and now.hour == 9 and now.minute == 0:
            await haftalik_yuborish(bot)
        await asyncio.sleep(60)

async def eslatma_yuborish(bot: Bot):
    from database import get_db
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
    dp.include_router(bellashuv.router)
    dp.include_router(yutuqlar.router)
    dp.include_router(haftalik.router)
    dp.include_router(sevimli.router)
    
    asyncio.create_task(motivatsiya_yuborish(bot))
    asyncio.create_task(haftalik_yuborish_task(bot))
    asyncio.create_task(eslatma_yuborish(bot))
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
