import asyncio
import json

from copy import deepcopy
from pathlib import Path
from typing import Any


class JsonStorage:
    
    DEFAULT_DATA = {
        "settings": {},
        "accounts": []
    }
    
    def __init__(self, file_path: str | Path = "config.json"):
        self.file_path = (
            Path(file_path)
            if file_path is not None
            else Path(__file__).resolve().parent / "config.json"
        )
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
        
        if (not self.file_path.exists() or self.file_path.stat().st_size == 0 or self._read_sync(self.file_path) == {}):
            self._write_sync(self.file_path, deepcopy(self.DEFAULT_DATA))
            
    
    @staticmethod
    def _read_sync(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)


    @staticmethod
    def _write_sync(path: Path, data: dict[str, Any]) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(path)


    async def read(self) -> dict[str, Any]:
        async with self._lock:
            return deepcopy(self._read_sync(self.file_path))


    async def write(self, data: dict[str, Any]) -> None:
        async with self._lock:
            self._write_sync(self.file_path, data)
            