
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import Channel
from app.core.security import get_current_user

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("/")
def get_channels(
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    rows = session.exec(select(Channel).order_by(Channel.channel)).all()
    return {row.channel: row.name for row in rows}


@router.post("/")
def set_channel(
    data: Channel,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    if data.channel < 1 or data.channel > 12:
        raise HTTPException(400, "channel harus 1..12")

    row = session.exec(
        select(Channel).where(Channel.channel == data.channel)
    ).first()

    if row:
        row.name = data.name
    else:
        session.add(Channel(channel=data.channel, name=data.name))

    session.commit()
    return {"ok": True}
