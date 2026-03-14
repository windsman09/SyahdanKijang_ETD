# app/db/models.py
from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint

# ---- ENUM untuk io_type ----
class IOType(str, Enum):
    coil = "coil"
    holding = "holding"

# ---- User ----
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True

# ---- Device (multi-device) ----
class Device(SQLModel, table=True):
    __tablename__ = "device"
    __table_args__ = (UniqueConstraint("name", name="uq_device_name"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    ip: str
    port: int = 5000
    unit: int = 1
    io_type: IOType = Field(default=IOType.coil)
    channels: int = 12
    timeout: float = 5.0
    retries: int = 3
    enabled: bool = True

# ---- Channel (per device) ----
class Channel(SQLModel, table=True):
    __tablename__ = "channels"
    __table_args__ = (UniqueConstraint("device_id", "channel", name="uq_device_channel"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: int = Field(foreign_key="device.id", index=True)
    channel: int = Field(index=True)  # 1..N per device
    name: str

# ---- Item (KEMBALIKAN INI) ----
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
