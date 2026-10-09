from aiogram import Router

from app.session import SessionManager
from app.utils.storage import JsonStorage


class AccountsListHandler:
    def __init__(self, storage: JsonStorage, telethon_manager: SessionManager):
        self.storage = storage
        self.telethon_manager = telethon_manager
        
        
    def register(self, router: Router) -> None:
        router.callback_query.register(self.accounts_list, F.data == "accounts_list")
        