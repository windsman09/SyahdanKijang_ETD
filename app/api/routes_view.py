from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import Channel, Device

router = APIRouter(tags=["views"])
templates = Jinja2Templates(directory="app/templates")

# =========================
# LOGIN PAGE
# =========================
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "title": "Login",
        }
    )
# =========================
# ETD DETAIL PAGE (DINAMIS)
# =========================
@router.get("/etd/{device_name}", response_class=HTMLResponse)
def etd_page(
    request: Request,
    device_name: str,
    session: Session = Depends(get_session),
):
    device = session.exec(
        select(Device).where(Device.name == device_name)
    ).first()

    channels = session.exec(
        select(Channel)
        .where(Channel.device_id == device.id)
        .order_by(Channel.channel)
    ).all() if device else []

    return templates.TemplateResponse(
        request=request,
        name="etd8a12.html",
        context={
            "request": request,
            "title": device_name,
            "device": device,
            "channels": channels,
        }
    )


# =========================
# API: GET CHANNELS (JSON)
# =========================
@router.get("/channels")
def get_channels(session: Session = Depends(get_session)):
    return session.exec(
        select(Channel).order_by(Channel.channel)
    ).all()

@router.get("/devices", response_class=HTMLResponse)
def list_devices(
    request: Request,
    session: Session = Depends(get_session),
):
    devices = session.exec(select(Device)).all()

    return templates.TemplateResponse(
        request=request,
       name= "devices.html",
        context={
            "request": request,
            "title": "Daftar Device",
            "devices": devices,
        }
    )
