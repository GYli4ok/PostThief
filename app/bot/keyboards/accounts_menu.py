from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.utils.chat_types import ChatType

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
        [
            InlineKeyboardButton(text="📥 Каналы получатели", callback_data=f"account_chats:{account_id}:target"),
            InlineKeyboardButton(text="📥 Каналы источники", callback_data=f"account_chats:{account_id}:source")
        ],
        [InlineKeyboardButton(text="🗑 Удалить аккаунт", callback_data=f"account_delete:{account_id}")],
        [InlineKeyboardButton(text="⏱ Настройка", callback_data=f"auto_forward:{account_id}")],
        [InlineKeyboardButton(text="⬅️ Аккаунты", callback_data="accounts")],
    ])
def chat_list_menu(channels: list[dict], account_id: str, selected_channels: list[int], channel_type: ChatType, page: int, per_page: int = 8) -> InlineKeyboardMarkup:
    start = page * per_page
    end = start + per_page
    rows = []
    selected_set = {int(channel_id) for channel_id in selected_channels}
    for channel in channels[start:end]:
        channel_id = int(channel["id"])
        checked = "✅" if channel_id in selected_set else "▫"
        rows.append([InlineKeyboardButton(
            text=f"{checked} 📢 {channel['title'][:32]}",
            callback_data=f"chat_toggle:{account_id}:{channel_type.value}:{channel['id']}"
        )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"chat_page:{account_id}:{channel_type.value}:{page-1}"))
    if end < len(channels):
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"chat_page:{account_id}:{channel_type.value}:{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="⬅️ Аккаунт", callback_data=f"account:{account_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
    
def auto_forward_menu(account_id: str, enabled: bool) -> InlineKeyboardMarkup:
    text = (
        "⏸ Выключить автокопирование"
        if enabled
        else "▶️ Включить автокопирование"
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=f"toggle_auto_forward:{account_id}"),],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"account:{account_id}")],
        ]
    )