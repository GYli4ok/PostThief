import asyncio
from io import BytesIO
import re
import uuid
import qrcode

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from telethon.errors import PhoneCodeExpiredError, PhoneCodeInvalidError, SessionPasswordNeededError\

from app.bot.keyboards.accounts_menu import account_menu, accounts_list_menu, chat_list_menu
from app.session import SessionManager
from app.utils.chat_types import ChatType, get_chat_type
from app.utils.states import AddAccountStates
from app.utils.storage import JsonStorage


class AccountHandlers:
    def __init__(self, storage: JsonStorage, tg: SessionManager) -> None:
        self.storage = storage
        self.tg = tg

    def register(self, router: Router) -> None:
            router.callback_query.register(self.account, F.data.startswith("account:"))
            router.callback_query.register(self.account_chats, F.data.startswith("account_chats:"))
            router.callback_query.register(self.chat_page, F.data.startswith("chat_page:"))
            router.callback_query.register(self.chat_toggle, F.data.startswith("chat_toggle:"))
            
    async def account(self, callback: CallbackQuery, state: FSMContext):
        account_id = callback.data.split(":", 1)[1]
        await state.clear()
        await state.update_data(account_id=account_id)

        await self.show_account(callback, account_id)
        
    async def show_account(self, callback: CallbackQuery, account_id):
        account = await self.storage.get_account(account_id)

        if not account:
            await callback.answer("❌ Аккаунт не найден.", show_alert=True)
            return

        await callback.message.edit_text(
            f"👤 Аккаунт: <b>{account['display_name']}</b>\n"
            f"Телеграм ID: <code>{account['telegram_id']}</code>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "<b>📥 Канал-источник</b>\n"
            "└ Откуда копируются сообщения\n"
            "<b>📤 Канал-получатель</b>\n"
            "└ Куда отправляются сообщения\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "<b>⚙️ УПРАВЛЕНИЕ АККАУНТОМ</b>\n"
            "Выберите действие с помощью кнопок ниже 👇",
            reply_markup=account_menu(account_id),
            parse_mode="HTML",
        )
        
    async def show_chat_page(self, callback: CallbackQuery, account_id: str, channel_type: ChatType, page: int):
        item = await self.storage.get_account(account_id)
        if not item:
            await callback.answer("Аккаунт не найден", show_alert=True)
            return
        try:
            target_channels, source_channels = await self.tg.get_list_channels(account_id)
            target_selected_channels = item.get("target_channels", [])
            source_selected_channels = item.get("source_channels", [])
        except Exception as e:
            await callback.answer(f"Ошибка: {e}", show_alert=True)
            return
        
        channels = source_channels if channel_type == ChatType.SOURCE else target_channels
        selected = source_selected_channels if channel_type == ChatType.SOURCE else target_selected_channels
        
        await callback.message.edit_text(
            "📋 <b>УПРАВЛЕНИЕ КАНАЛАМИ</b>\n\n"
            "📊 <b>СТАТИСТИКА</b>\n"
            f"├ 📚 Всего доступно: <b>{len(target_channels) + len(source_channels)}</b>\n"
            f"├ 📥 Источники: <b>{len(source_channels)}</b>\n"
            f"└ 📤 Получатели: <b>{len(target_channels)}</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "✅ — Канал выбран для использования\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "👇<b>Нажимайте на канал</b>, чтобы добавить его в список или убрать из него.",
            reply_markup=chat_list_menu(channels, account_id, selected, channel_type, page),
            parse_mode="HTML",
        )
        await callback.answer()

    async def account_chats(self, callback: CallbackQuery):
        _, account_id, raw_channel_type = callback.data.split(":", 2)
        try:
            channel_type = get_chat_type(raw_channel_type)
        except ValueError:
            await callback.answer(
                "Среди списка есть неизвестный тип чата",
                show_alert=True
            )
            return
        await self.show_chat_page(callback, account_id, channel_type, 0)
        
    async def chat_page(self, callback: CallbackQuery):
        _, account_id, raw_channel_type, page = callback.data.split(":", 3)
        try:
            channel_type = get_chat_type(raw_channel_type)
        except ValueError:
            await callback.answer(
                "Среди списка есть неизвестный тип чата",
                show_alert=True
            )
            return
        await self.show_chat_page(callback, account_id, channel_type, int(page))
    
    async def chat_toggle(self, callback: CallbackQuery):
        _, account_id, raw_channel_type, channel_id = callback.data.split(":", 3)
        item = await self.storage.get_account(account_id)
        if not item:
            await callback.answer("Аккаунт не найден", show_alert=True)
            return
        try:
            channel_type = get_chat_type(raw_channel_type)
        except ValueError:
            await callback.answer(
                "Среди списка есть неизвестный тип чата",
                show_alert=True
            )
            return
        channel_name = ("📥 Каналы источники" if channel_type == ChatType.SOURCE else "📥 Каналы получатели")
        key = ("source_channels" if channel_type == ChatType.SOURCE else "target_channels")
        selected_channels = item.get(key, [])
        channel_id = int(channel_id)
        
        if channel_id in selected_channels:
            print(f"Channel remove list")
            selected_channels.remove(channel_id)
            message = f"🗑 Канал удалён из списка:\n {channel_name}"
        else:
            print(f"Channel added list")
            selected_channels.append(channel_id)
            message = f"✅ Канал добавлен в список:\n {channel_name}"
        
        await self.storage.update_account(account_id, {key: selected_channels})
        await self.show_account(callback, account_id)
        await callback.answer(message, show_alert=True)
        
class LogInAccountHandlers:
    def __init__(self, storage: JsonStorage, tg: SessionManager) -> None:
        self.storage = storage
        self.tg = tg

    def register(self, router: Router) -> None:
            router.callback_query.register(self.account_add, F.data == "account_add")
            router.callback_query.register(self.account_add_qr, F.data == "account_add_qr")
            router.message.register(self.account_phone, AddAccountStates.phone)
            router.message.register(self.account_code, AddAccountStates.code)
            router.message.register(self.account_password, AddAccountStates.password)
    
    def clean_phone(self, value: str) -> str:
        return re.sub(r"[^\d+]", "", value.strip())
    
### Save authorized account to storage    
    async def save_authorized_account(self, account_id: str, me):
        phone = me.phone or "Не указан"
        display_name = " ".join(filter(None, [me.first_name, me.last_name])).strip()
        if not display_name:
            display_name = f"@{me.username}" if me.username else phone
        
        account = {
            "account_id": account_id,
            "telegram_id": me.id,
            "auto_forward": False,
            "phone": me.phone or "Не указан",
            "display_name": display_name,
            "path_session": str(self.tg.session_path(account_id)),
            "source_channels": [],
            "target_channels": []
        }
        await self.storage.add_account(account)
        
        return display_name 
    
### Login with QR code and phone number handlers
    async def account_add_qr(self, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        await callback.message.edit_text("🔄 Загрузка QR-кода...")
        account_id = uuid.uuid4().hex[:12]
        client = self.tg.client(account_id)
        try:
            await client.connect()
            qr_login = await client.qr_login()
            buffer = BytesIO()
            qrcode.make(qr_login.url).save(buffer, format="PNG")
            photo = BufferedInputFile(buffer.getvalue(), filename="telegram_login_qr.png")

            await callback.message.delete()
            await callback.message.answer_photo(
                photo=photo,
                caption=(
                    "🔳 <b>Вход в Telegram по QR-коду</b>\n\n"
                    "Открой Telegram на устройстве, где аккаунт "
                    "уже авторизован, и отсканируй QR-код "
                    "через раздел «Устройства».\n\n"
                    "QR-код временный. Если срок истечёт, "
                    "запусти вход заново."
                ),
                parse_mode="HTML",
            )
            
            try:
                await qr_login.wait(timeout=40)
            except SessionPasswordNeededError:
                await client.disconnect()
                await state.set_state(AddAccountStates.password)
                await state.update_data(account_id=account_id)
                await callback.message.answer(
                    "🔐 На аккаунте включена двухэтапная аутентификация.\n\n"
                    "Отправьте пароль 2FA. Он будет использован только для входа и не будет сохранён."
                )
                return
            
            
            me = await client.get_me()
            await client.disconnect()
            display_name = await self.save_authorized_account(account_id, me)
            await state.clear()
            await callback.message.answer(f"✅ Аккаунт подключён:\n<b>{display_name}</b>", parse_mode="HTML")
            
        except asyncio.TimeoutError:
            await client.disconnect()
            await self.tg.delete_session(account_id)
            await callback.message.answer("⌛ QR-код истёк. Нажми кнопку входа и создай новый.")
            return
        except Exception as e:
            await client.disconnect()
            await self.tg.delete_session(account_id)
            await callback.message.answer(f"❌ Ошибка входа:\n<code>{e}</code>", parse_mode="HTML")
            return

### Login with phone number handlers     
    async def account_add(self, callback: CallbackQuery, state: FSMContext):
        
        await state.clear()
        await state.set_state(AddAccountStates.phone)
        await callback.message.edit_text(
            "➕ <b>Добавление аккаунта</b>\n\n"
            "Отправьте номер телефона:\n"
            "Код Telegram и пароль 2FA не сохраняются.",
            parse_mode="HTML",
        )
        await callback.answer()

    async def account_phone(self, message: Message, state: FSMContext):

        phone = self.clean_phone(message.text or "")
        if not phone.startswith("+") or len(phone) < 8:
            await message.answer("❌ Неверный номер.", parse_mode="HTML")
            return

        account_id = uuid.uuid4().hex[:12]
        client = self.tg.client(account_id)
        await client.connect()
        try:
            sent = await client.send_code_request(phone)
        except Exception as e:
            await client.disconnect()
            await self.tg.delete_session(account_id)
            await message.answer(f"❌ Не удалось отправить код:\n<code>{e}</code>", parse_mode="HTML")
            return
        await client.disconnect()

        await state.update_data(account_id=account_id, phone=phone, phone_code_hash=sent.phone_code_hash)
        await state.set_state(AddAccountStates.code)
        await message.answer(
            "📩 Telegram отправил код подтверждения.\n\n"
            "Отправьте код сюда. Например: <code>12345</code>",
            parse_mode="HTML",
        )

    async def account_code(self, message: Message, state: FSMContext):

        code = re.sub(r"\D", "", message.text or "")
        data = await state.get_data()
        account_id = data["account_id"]
        phone = data["phone"]

        client = self.tg.client(account_id)
        await client.connect()
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=data["phone_code_hash"])
        except SessionPasswordNeededError:
            await client.disconnect()
            await state.set_state(AddAccountStates.password)
            await message.answer(
                "🔐 На аккаунте включена двухэтапная аутентификация.\n\n"
                "Отправьте пароль 2FA. Он будет использован только для входа и не будет сохранён."
            )
            return
        except PhoneCodeInvalidError:
            await client.disconnect()
            await message.answer("❌ Неверный код. Попробуйте ещё раз.")
            return
        except PhoneCodeExpiredError:
            await client.disconnect()
            await self.tg.delete_session(account_id)
            await state.clear()
            await message.answer("❌ Код истёк. Начните добавление аккаунта заново.")
            return
        except Exception as e:
            await client.disconnect()
            await self.tg.delete_session(account_id)
            await message.answer(f"❌ Ошибка входа:\n<code>{e}</code>", parse_mode="HTML")
            return
        
        me = await client.get_me()
        await client.disconnect()
        display_name = await self.save_authorized_account(account_id, me)
        await state.clear()
        await message.answer(f"✅ Аккаунт подключён:\n<b>{display_name}</b>", parse_mode="HTML")

    async def account_password(self, message: Message, state: FSMContext):
        data = await state.get_data()
        account_id = data["account_id"]
        client = self.tg.client(account_id)
        await client.connect()
        try:
            await client.sign_in(password=message.text or "")
            me = await client.get_me()
        except Exception as e:
            await client.disconnect()
            await message.answer(
                f"❌ Не удалось пройти 2FA.\n<code>{e}</code>\n\nПроверьте пароль и попробуйте ещё раз.",
                parse_mode="HTML",
            )
            return
        await client.disconnect()
        display_name = await self.save_authorized_account(account_id, me)
        await state.clear()
        await message.answer(f"✅ Аккаунт подключён:\n<b>{display_name}</b>", parse_mode="HTML")
        

