from aiogram.types import CallbackQuery
from aiogram import F, Router
from telethon import events

from app.bot.keyboards.accounts_menu import auto_forward_menu


class AutoForwardManager:
    def __init__(self, tg, storage):
        self.tg = tg
        self.storage = storage
        self.handlers = {}
        
    def register(self, router: Router) -> None:
        router.callback_query.register(self.auto_forward, F.data.startswith("auto_forward:"))
        router.callback_query.register(self.toggle_auto_forward, F.data.startswith("toggle_auto_forward:"))
        
    async def start(self, account_id: str):
        if account_id in self.handlers:
            return
        
        account = await self.storage.get_account(account_id)

        if not account:
            raise ValueError("Аккаунт не найден")

        sources = [int(x) for x in account.get("source_channels", [])]
        targets = [int(x) for x in account.get("target_channels", [])]

        if not sources:
            raise ValueError("Не выбраны каналы-источники")
        if not targets:
            raise ValueError("Не выбраны каналы-получатели")

        client = self.tg.client(account_id)
        await client.connect()

        if not await client.is_user_authorized():
            raise RuntimeError("Аккаунт Telegram не авторизован")

        async def on_new_post(event):
            message = event.message

            for target_id in targets:
                if message.media:
                    await client.send_file(
                        target_id,
                        message.media,
                        caption=message.message or "",
                    )
                elif message.message:
                    await client.send_message(
                        target_id,
                        message.message,
                    )

        client.add_event_handler(on_new_post, events.NewMessage(chats=sources))
        self.handlers[account_id] = (client, on_new_post, sources)
        
    async def stop(self, account_id: str):
        data = self.handlers.pop(account_id, None)

        if data is None:
            return

        client, handler, _ = data
        client.remove_event_handler(handler)
        
    async def toggle_auto_forward(self, callback: CallbackQuery):
        account_id = callback.data.split(":", 1)[1]
        
        account = await self.storage.get_account(account_id)
        
        if not account:
            await callback.answer(
                "Аккаунт не найден",
                show_alert=True,
            )
            return
        
        enabled = account.get("auto_forward", False)
        
        try:
            if enabled:
                await self.stop(account_id)
                enabled = False
            else:
                await self.start(account_id)
                enabled = True
        
            await self.storage.update_account(account_id, {"auto_forward": enabled})
        
        except Exception as e:
            await callback.answer(
                f"Не удалось изменить настройку: {e}",
                show_alert=True,
            )
            return
        
        await callback.answer(
            "Автокопирование включено"
            if enabled
            else "Автокопирование выключено"
        )
        
        await callback.message.edit_reply_markup(
            "Включить\Выключить автокопирование",
            reply_markup=auto_forward_menu(account_id, enabled),
        )
        
    async def auto_forward(self, callback: CallbackQuery):
        account_id = callback.data.split(":", 1)[1]

        account = await self.storage.get_account(account_id)

        if not account:
            await callback.answer(
                "Аккаунт не найден",
                show_alert=True,
            )
            return
        
        enabled = account.get("auto_forward", False)
        
        await callback.message.edit_text(
            "Включить\Выключить автокопирование",
            reply_markup=auto_forward_menu(account_id, enabled),
        )