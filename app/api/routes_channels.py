
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import Channel
from app.core.security import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/channels", tags=["channels"])


# =========================
# Schema (Request Body)
# =========================

class ChannelRename(BaseModel):
    device_id: int
    channel: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=100)


# =========================
# GET channels per device
# =========================

@router.get("/{device_id}")
def get_channels(
    device_id: int,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    rows = session.exec(
        select(Channel)
        .where(Channel.device_id == device_id)
        .order_by(Channel.channel)
    ).all()

    return [
        {
            "channel": row.channel,
            "name": row.name,
        }
        for row in rows
    ]


# =========================
# RENAME channel
# =========================

@router.put("/rename")
def rename_channel(
    data: ChannelRename,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    row = session.exec(
        select(Channel)
        .where(Channel.device_id == data.device_id)
        .where(Channel.channel == data.channel)
    ).first()

    if not row:
        raise HTTPException(status_code=404, detail="Channel tidak ditemukan")

    row.name = data.name

    session.add(row)
    session.commit()
    session.refresh(row)

    return {
        "device_id": row.device_id,
        "channel": row.channel,
        "name": row.name,
    }
