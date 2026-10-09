
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.utils.storage import JsonStorage
from app.bot.keyboards.main_menu import menu


class MainHandlers:
    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def register(self, router: Router) -> None:
        router.message.register(self.start, CommandStart())
        router.callback_query.register(self.menu, F.data == "menu")
            
    async def start(self, message: Message) -> None:
        await message.answer(
            'Добро пожаловать в PostThief! 👋\n\n',
            reply_markup=menu(),
            parse_mode="HTML",
        )
    async def menu(self, callback: CallbackQuery) -> None:
        await callback.message.edit_text(
            'Добро пожаловать в PostThief! 👋\n\n',
            reply_markup=menu(),
            parse_mode="HTML",
        )