import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _parse_admin_ids(value: str) -> set[int]:
    result: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if part:
            result.add(int(part))
    return result


@dataclass(frozen=True)
class Config:
    shop_bot_token: str
    telethon_api_id: int
    telethon_api_hash: str
    admin_ids: set[int]


def load_config() -> Config:
    tg_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    telethon_api_id = int(os.getenv("TELETHON_API_ID", 0))
    telethon_api_hash = os.getenv("TELETHON_API_HASH", "")
    admin_ids = _parse_admin_ids(os.getenv("ADMIN_IDS", ""))

    if not tg_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не указан в .env")

    if not telethon_api_id:
        raise RuntimeError("TELETHON_API_ID не указан в .env")

    if not telethon_api_hash:
        raise RuntimeError("TELETHON_API_HASH не указан в .env")

    return Config(
        shop_bot_token=tg_bot_token,
        telethon_api_id=telethon_api_id,
        telethon_api_hash=telethon_api_hash,
        admin_ids=admin_ids
    )
