from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List
from starlette import status

from app.core.security import get_current_user
from app.db.session import get_session
from app.db.models import Device
from app.services.modbus_client import ModbusService

router = APIRouter(prefix="/api/etd", tags=["etd"])


# =========================
# Pydantic Models
# =========================
class ChannelWrite(BaseModel):
    channel: int = Field(..., ge=1)
    on: bool


class ChannelRange(BaseModel):
    start: int = Field(..., ge=1)
    count: int = Field(..., ge=1)


# =========================
# Helpers
# =========================
def get_device(device_id: int) -> Device:
    with next(get_session()) as session:
        device = session.get(Device, device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device tidak ditemukan",
            )
        return device


def make_modbus_service(device: Device) -> ModbusService:
    return ModbusService(
        host=device.ip,
        port=device.port,
        slave_id=device.unit,
        timeout=device.timeout,
        retries=device.retries,
    )


ETD_OUTPUT_ON = 0x0100
ETD_OUTPUT_OFF = 0x0200


# =========================
# Routes
# =========================
@router.get("/channels")
async def get_channels(user=Depends(get_current_user)):
    return [{"index": i, "name": f"CH {i}"} for i in range(1, 13)]


@router.get("/devices/{device_id}/outputs", response_model=List[bool])
async def get_outputs(
    device_id: int,
    user=Depends(get_current_user),
):
    device = get_device(device_id)
    svc = make_modbus_service(device)

    try:
        states: List[bool] = []

        for addr in range(device.channels):
            regs = await svc.read_holding_registers(addr)
            v = regs[0]
            states.append(v in (1, ETD_OUTPUT_ON, True))

        return states

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"modbus read failed device={device.name} ip={device.ip}: {e}",
        )


@router.post("/devices/{device_id}/outputs/set")
async def set_output(
    device_id: int,
    req: ChannelWrite,
    user=Depends(get_current_user),
) -> dict:
    device = get_device(device_id)
    svc = make_modbus_service(device)

    addr = req.channel - 1
    value = ETD_OUTPUT_ON if req.on else ETD_OUTPUT_OFF

    try:
        await svc.write_single_register(addr, value)
        return {"ok": True, "channel": req.channel, "requested_on": req.on}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"modbus write failed device={device.name} ip={device.ip}: {e}",
        )
