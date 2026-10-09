from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Аккаунты", callback_data="accounts")],
            [InlineKeyboardButton(text="➕ Добавить акаунт", callback_data="account_add")],
        ]
    )


