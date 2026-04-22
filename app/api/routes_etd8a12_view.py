
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import Channel, Device

router = APIRouter(tags=["views"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/etd/{device_name}", response_class=HTMLResponse)
def etd_page(
    request: Request,
    device_name: str,
    session: Session = Depends(get_session),
):
    device = session.exec(
        select(Device).where(Device.name == device_name)
    ).first()

    channels = []
    if device:
        channels = session.exec(
            select(Channel)
            .where(Channel.device_id == device.id)
            .order_by(Channel.channel)
        ).all()

    return templates.TemplateResponse(
        "etd8a12.html",
        {
            "request": request,
            "title": device_name,
            "device": device,
            "channels": channels,
        }
    )
