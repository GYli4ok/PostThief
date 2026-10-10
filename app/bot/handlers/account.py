import asyncio
from io import BytesIO
import re
import uuid
import qrcode

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from telethon.errors import PhoneCodeExpiredError, PhoneCodeInvalidError, SessionPasswordNeededError

from app.bot.keyboards.accounts_menu import account_menu
from app.session import SessionManager
from app.utils.states import AddAccountStates
from app.utils.storage import JsonStorage


class AccountHandlers:
    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def register(self, router: Router) -> None:
            router.callback_query.register(self.account, F.data.startswith("account:"))
            
    async def account(self, callback: CallbackQuery, state: FSMContext):
        account_id = callback.data.split(":", 1)[1]
        account = await self.storage.get_account(account_id)
        if not account:
            await callback.answer()
            await callback.answer("❌ Аккаунт не найден.", show_alert=True)
            return

        await state.clear()
        await state.update_data(account_id=account_id)
        await callback.message.edit_text(
            f"👤 Аккаунт: <b>{account['display_name']}</b>\n\n"
            f"Телеграм ID: <code>{account['telegram_id']}</code>\n"
            f"Номер телефона: <code>{account['phone']}</code>\n\n"
            "Выберите действие:",
            reply_markup=account_menu(account_id),
            parse_mode="HTML",
        )
            

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
            "phone": me.phone or "Не указан",
            "display_name": display_name,
            "path_session": str(self.tg.session_path(account_id)),
            "source_channel": [],
            "target_channel": []
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
        

