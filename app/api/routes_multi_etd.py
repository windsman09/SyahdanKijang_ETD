# app/api/routes_multi_etd.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.db.session import get_session
from app.db.models import Device, Channel
from app.services.modbus_client import ModbusService

router = APIRouter(prefix="/devices", tags=["devices"])

def _get_device_or_404(session: Session, device_id: int) -> Device:
    d = session.get(Device, device_id)
    if not d or not d.enabled:
        raise HTTPException(status_code=404, detail="device not found / disabled")
    return d

def _svc(d: Device) -> ModbusService:
    return ModbusService(
        host=d.ip, port=d.port, unit_id=d.unit,
        timeout=d.timeout, retries=d.retries
    )

@router.get("/", response_model=List[Device])
def list_devices(session: Session = Depends(get_session), user=Depends(get_current_user)):
    return session.exec(select(Device).order_by(Device.name)).all()

@router.get("/{device_id}/channels")
def get_channels(device_id: int, session: Session = Depends(get_session), user=Depends(get_current_user)):
    d = _get_device_or_404(session, device_id)
    rows = session.exec(
        select(Channel).where(Channel.device_id == d.id).order_by(Channel.channel)
    ).all()
    if not rows:
        return [{"index": i, "name": f"CH {i}"} for i in range(1, d.channels + 1)]
    return [{"index": r.channel, "name": r.name} for r in rows]

@router.get("/{device_id}/outputs", response_model=List[bool])
async def get_outputs(device_id: int, session: Session = Depends(get_session), user=Depends(get_current_user)):
    d = _get_device_or_404(session, device_id)
    svc = _svc(d)
    try:
        if d.io_type == "coil":
            coils = await svc.read_coils(address=0, count=d.channels)
            return [bool(v) for v in coils]
        else:
            regs = await svc.read_holding_registers(address=0, count=d.channels)
            # mapping generik; sesuaikan nilai devicenya
            return [(v in (1, 0x0100, True)) for v in regs]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"modbus read failed host={d.ip} port={d.port} unit={d.unit}: {e}")

class WriteBody(BaseModel):
    channel: int = Field(ge=1)
    on: bool

@router.post("/{device_id}/outputs/set")
async def set_output(device_id: int, body: WriteBody, session: Session = Depends(get_session), user=Depends(get_current_user)):
    d = _get_device_or_404(session, device_id)
    if body.channel > d.channels:
        raise HTTPException(status_code=400, detail=f"channel harus 1..{d.channels}")

    svc = _svc(d)
    addr = body.channel - 1
    try:
        if d.io_type == "coil":
            ok = await svc.write_single_coil(address=addr, value=body.on)
        else:
            value = 0x0100 if body.on else 0x0200
            ok = await svc.write_single_register(address=addr, value=value)
        return {"ok": bool(ok)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"modbus write failed host={d.ip} port={d.port} unit={d.unit} ch={body.channel}: {e}")
