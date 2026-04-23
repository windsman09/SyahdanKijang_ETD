from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from app.db.session import get_session
from app.db.models import Device
from app.utils.exceptions import not_found
from app.core.security import get_current_user

router = APIRouter(prefix="/devices", tags=["devices"])
templates = Jinja2Templates(directory="app/templates")


class DeviceIn(BaseModel):
    name: str = Field(min_length=1)
    ip: str
    enabled: bool = True


# =========================
# API JSON (AUTH)
# =========================
@router.get("/")
async def list_devices(
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    return session.exec(select(Device)).all()


@router.post("/", response_model=Device)
async def create_device(
    data: DeviceIn,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    row = Device(**data.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


# =========================
# HTML PAGE (NO AUTH)
# =========================
@router.get("/{device_id}/page", response_class=HTMLResponse)
async def device_page(
    device_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    device = session.get(Device, device_id)
    if not device:
        raise not_found(f"Device {device_id} tidak ditemukan")

    return templates.TemplateResponse(
        "devices.html",
        {
            "request": request,
            "device": device,
        }
    )
