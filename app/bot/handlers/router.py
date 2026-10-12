from aiogram import Router

from app.session import SessionManager
from app.bot.handlers import MainHandlers, LogInAccountHandlers, AccountsListHandler, AccountHandlers, AutoForwardManager
from app.utils.storage import JsonStorage


def setup(storage: JsonStorage, tg: SessionManager) -> Router:
    router = Router()

    MainHandlers(storage).register(router)
    LogInAccountHandlers(storage, tg).register(router)
    AccountHandlers(storage, tg).register(router)
    AccountsListHandler(storage).register(router)
    AutoForwardManager(tg, storage).register(router)
    
    return router