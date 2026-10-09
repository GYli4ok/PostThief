from aiogram import Router

from app.session import TelethonManager
from app.bot.handlers import MainHandlers, AccountHandlers
from app.utils.storage import JsonStorage


def setup(storage: JsonStorage, tg: TelethonManager) -> Router:
    router = Router()

    MainHandlers(storage).register(router)
    AccountHandlers(storage, tg).register(router)
    
    return router