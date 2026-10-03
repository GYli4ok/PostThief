from aiogram import F, Router
from aiogram.types import Message

from app.utils.storage import JsonStorage


class AccountHandlers:
    def __init__(self, storage: JsonStorage):
        self.storage = storage
        
    def register(self, router: Router) -> None:
            router.callback_query.register(self.accounts, F.data == "accounts")
            
    async def accounts(self, message: Message) -> None:
        
        data = await self.storage.read()
        accounts = data["accounts"]
        
        if not accounts:
            await message.answer("У вас нет добавленных аккаунтов.")
            return

        account_list = "\n".join([f"{i + 1}. {account}" for i, account in enumerate(accounts)])
        await message.answer(f"Ваши аккаунты:\n{account_list}")