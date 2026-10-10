from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.bot.keyboards.accounts_menu import accounts_list_menu
from app.utils.storage import JsonStorage


class AccountsListHandler:
    def __init__(self, storage: JsonStorage,):
        self.storage = storage
        
        
    def register(self, router: Router) -> None:
        router.callback_query.register(self.accounts, F.data == "accounts")
        
    async def accounts(self, callback: CallbackQuery):   
       await callback.message.edit_text(
           "🔘 Список аккаунтов:",
           reply_markup=accounts_list_menu(await self.storage.get_accounts()),
           parse_mode="HTML",
        )
        
    