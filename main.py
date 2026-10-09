import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.session import SessionManager
from app.utils.storage import JsonStorage
from app.bot.handlers import setup
from env import load_config

async def main():
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    storage = JsonStorage()
    
    
    bot = Bot(config.shop_bot_token)
    dp = Dispatcher()
    
    tg = SessionManager(config.telethon_api_id, config.telethon_api_hash)
    
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(setup(storage, tg))
    await dp.start_polling(bot) 
    
if __name__ == "__main__":
    asyncio.run(main())