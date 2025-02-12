from typing import Optional, List
from pydantic import HttpUrl, BaseModel
from datetime import datetime
from enum import Enum


class Roles(Enum):
    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"


class Message(BaseModel):
    role: Roles
    content: str


class DatabaseEnum(Enum):
    MYSQL = "mysql"
    VECTORDB = "vectordb"


class GraphState(BaseModel):
    messages: List[Message]
    database: Optional[DatabaseEnum] = DatabaseEnum.VECTORDB
    query: Optional[str] = None
    sql_query: Optional[str] = None
