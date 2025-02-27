from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel
from typing_extensions import TypedDict, Annotated

class QueryOutput(TypedDict):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."]

class DatabaseEnum(str, Enum):
    MYSQL = "mysql"
    VECTORDB = "vectordb"

class Message(BaseModel):
    role: str
    content: str

class GraphState(BaseModel):
    messages: List[Dict[str, str]]
    query: Optional[str] = None
    sql_query: Optional[str] = None
    result: Optional[str] = None
    visualization: Optional[Dict] = {"show": False}