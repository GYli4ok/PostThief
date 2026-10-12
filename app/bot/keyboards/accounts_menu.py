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
        [InlineKeyboardButton(text="⏱ Настройка", callback_data=f"auto_forward:{account_id}")],
        [InlineKeyboardButton(text="⬅️ Аккаунты", callback_data="accounts")],
    ])
def chat_list_menu(chats: list[dict], account_id: str, selected_chats: list[int], page: int, per_page: int = 8) -> InlineKeyboardMarkup:
    start = page * per_page
    end = start + per_page
    rows = []
    selected_set = set(selected_chats)

    for chat in chats[start:end]:
        checked = "✅" if chat["id"] in selected_set else "▫️"
        rows.append([InlineKeyboardButton(
            text=f"{checked} 📢 {chat['title'][:32]}",
            callback_data=f"chat_toggle:{account_id}:{chat['id']}:{page}"
        )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"chat_page:{account_id}:{page-1}"))
    if end < len(chats):
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"chat_page:{account_id}:{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="⬅️ Аккаунт", callback_data=f"account:{account_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def channel_selected_type_menu(account_id: str, chatid: int, page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Канал-источник", callback_data=f"source_chat:{account_id}:{chatid}")],
        [InlineKeyboardButton(text="📤 Канал-получатель", callback_data=f"target_chat:{account_id}:{chatid}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"chat_page:{account_id}:{page}")],
    ])
def auto_forward_menu(
    account_id: str,
    enabled: bool,
) -> InlineKeyboardMarkup:
    text = (
        "⏸ Выключить автокопирование"
        if enabled
        else "▶️ Включить автокопирование"
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"auto_forward:{account_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=f"account:{account_id}",
                )
            ],
        ]
    )