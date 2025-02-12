from pydantic import BaseModel
from enum import Enum


class Roles(Enum):
    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"


class Message(BaseModel):
    role: Roles
    content: str
