from aiogram import Router

from app.bot.handlers import MainHandlers, AccountHandlers
from app.utils.storage import JsonStorage


def setup(storage: JsonStorage) -> Router:
    router = Router()

    MainHandlers(storage).register(router)
    AccountHandlers(storage).register(router)
    
    return router