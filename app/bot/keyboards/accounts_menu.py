from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def accounts_list_menu(accounts: dict) -> InlineKeyboardMarkup:
    rows = []
    for account_id, item in accounts.items():
        label = item.get("display_name") or item.get("phone") or account_id
        rows.append([InlineKeyboardButton(text=f"👤 {label}", callback_data=f"account:{account_id}")])
    rows.append([InlineKeyboardButton(text="➕ Добавить аккаунт", callback_data="open_add_account_menu")])
    rows.append([InlineKeyboardButton(text="⬅️ Главное меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def account_menu(account_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Каналы и группы", callback_data=f"account_chats:{account_id}")],
        [InlineKeyboardButton(text="➕ Добавить чат", callback_data=f"account_add_chat:{account_id}")],
        [InlineKeyboardButton(text="🗑 Удалить аккаунт", callback_data=f"account_delete:{account_id}")],
        [InlineKeyboardButton(text="⏱ Настройка", callback_data=f"auto_settings:{account_id}")],
        [InlineKeyboardButton(text="⬅️ Аккаунты", callback_data="accounts")],
    ])
