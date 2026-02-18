
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True


class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    ip: str
    enabled: bool = True


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


# ✅ TAMBAHKAN INI
class Channel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    channel: int = Field(index=True, unique=True)  # 1..12
    name: str
