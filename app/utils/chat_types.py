from enum import Enum

class ChatType(str, Enum):
    SOURCE = "source"
    TARGET = "target"


def get_chat_type(value: str) -> ChatType:
    try:
        return ChatType(value)
    except ValueError:
        raise ValueError(f"Неизвестный тип чата: {value}")