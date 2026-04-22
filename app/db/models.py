# app/db/models.py

# app/db/models.py
from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint
from sqlalchemy import Enum as SAEnum

# ---- ENUM untuk io_type ----
class IOType(str, Enum):
    coil = "coil"
    holding = "holding"

# ---- User ----
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(
        nullable=False,
        index=True,
        unique=True,
        max_length=50
    )
    full_name: Optional[str] = Field(default=None, max_length=100)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)

# ---- Device (multi-device) ----
class Device(SQLModel, table=True):
    __tablename__ = "device"
    __table_args__ = (UniqueConstraint("name", name="uq_device_name"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, index=True)
    ip: str = Field(nullable=False, max_length=50)
    port: int = Field(default=5000)
    unit: int = Field(default=1)

    io_type: IOType = Field(
        default=IOType.coil,
        sa_type=SAEnum(IOType),
        nullable=False
    )

    channels: int = Field(default=12)
    timeout: float = Field(default=5.0)
    retries: int = Field(default=3)
    enabled: bool = Field(default=True)

    def __repr__(self):
        return f"<Device {self.name} ({self.ip})>"

# ---- Channel (per device) ----
class Channel(SQLModel, table=True):
    __tablename__ = "channels"
    __table_args__ = (
        UniqueConstraint("device_id", "channel", name="uq_device_channel"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: int = Field(
        foreign_key="device.id",
        index=True,
        nullable=False
    )
    channel: int = Field(nullable=False, index=True)
    name: str = Field(nullable=False, max_length=100)

# ---- Item ----
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, max_length=100)
