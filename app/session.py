from pathlib import Path

from telethon import TelegramClient

class SessionManager:
    def __init__(self, api_id: int, api_hash: str, sessions_dir: str | Path = "sessions"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def session_path(self, account_id: str) -> str:
        return str(self.sessions_dir / account_id)

    async def client(self, account_id: str) -> TelegramClient:
        return TelegramClient(self.session_path(account_id), self.api_id, self.api_hash)
    
    async def delete_session(self, account_id: str) -> None:
        for path in self.sessions_dir.glob(f"{account_id}.session*"):
            try:
                path.unlink()
            except FileNotFoundError:
                pass