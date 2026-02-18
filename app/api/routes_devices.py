from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from app.db.session import get_session
from app.db.models import Device
from app.utils.exceptions import not_found
from app.core.security import get_current_user

router = APIRouter(prefix="/devices", tags=["devices"])

class DeviceIn(BaseModel):
    name: str = Field(min_length=1)
    ip: str
    enabled: bool = True

@router.get("/")
async def list_devices(session: Session = Depends(get_session), user=Depends(get_current_user)):
    return session.exec(select(Device)).all()

@router.post("/", response_model=Device)
async def create_device(data: DeviceIn, session: Session = Depends(get_session), user=Depends(get_current_user)):
    row = Device(**data.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row

@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: int, session: Session = Depends(get_session), user=Depends(get_current_user)):
    row = session.get(Device, device_id)
    if not row:
        raise not_found(f"Device {device_id} tidak ditemukan")
    return row
