from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Аккаунты", callback_data="accounts")],
            [InlineKeyboardButton(text="➕ Добавить акаунт", callback_data="open_add_account_menu")],
        ]
    )
def add_account_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔳 Войти по QR-коду", callback_data="account_add_qr")],
            [InlineKeyboardButton(text="📱 Войти по номеру", callback_data="account_add")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu")],
        ]
    )

