
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.utils.storage import JsonStorage
from app.bot.keyboards.main_menu import main_menu


class MainHandlers:
    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def register(self, router: Router) -> None:
        router.message.register(self.start, CommandStart())
            
    async def start(self, message: Message) -> None:
        await message.answer(
            'Добро пожаловать в PostThief! 👋\n\n',
            reply_markup=main_menu(),
            parse_mode="HTML",
        )