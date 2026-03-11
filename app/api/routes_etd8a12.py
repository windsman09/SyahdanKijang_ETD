
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

from app.core.security import get_current_user
from app.services.modbus_client import ModbusService

router = APIRouter(prefix="/etd8a12", tags=["etd8a12"])

# =========================
# Konfigurasi ETD / Modbus
# =========================
ETD_HOST = "10.21.240.5"
ETD_PORT = 5000
ETD_UNIT = 1

ETD_CHANNELS = 12  # CH1..CH12 → register 0..11

ETD_OUTPUT_ON  = 0x0100
ETD_OUTPUT_OFF = 0x0200

# =========================
# Modbus Service (singleton)
# =========================
_modbus_service = ModbusService(
    host=ETD_HOST,
    port=ETD_PORT,
    unit_id=ETD_UNIT,
    timeout=2.0,
    retries=2,
)

def svc() -> ModbusService:
    return _modbus_service

# =========================
# Models
# =========================
class ChannelWrite(BaseModel):
    channel: int = Field(..., ge=1, le=ETD_CHANNELS)
    on: bool

class ChannelRange(BaseModel):
    start: int = Field(..., ge=1, le=ETD_CHANNELS)
    count: int = Field(..., ge=1, le=ETD_CHANNELS)

# =========================
# Endpoints
# =========================
@router.get("/outputs", response_model=List[bool])
async def get_all_outputs(
    user=Depends(get_current_user),
) -> List[bool]:
    try:
        regs = await svc().read_holding_registers(
            address=0,
            count=ETD_CHANNELS
        )
        return [bool(v) for v in regs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )

@router.get("/outputs/{channel}", response_model=bool)
async def get_output(
    channel: int,
    user=Depends(get_current_user),
) -> bool:
    if not (1 <= channel <= ETD_CHANNELS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"channel harus 1..{ETD_CHANNELS}",
        )

    try:
        regs = await svc().read_holding_registers(
            address=channel - 1,
            count=1
        )
        return bool(regs[0])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )

@router.post("/outputs/set")
async def set_output(
    req: ChannelWrite,
    user=Depends(get_current_user),
) -> dict:
    addr = req.channel - 1
    value = ETD_OUTPUT_ON if req.on else ETD_OUTPUT_OFF

    try:
        ok = await svc().write_single_register(
            address=addr,
            value=value
        )
        return {
            "ok": ok,
            "channel": req.channel,
            "value": hex(value),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )

@router.post("/outputs/read-range", response_model=List[bool])
async def read_range(
    req: ChannelRange,
    user=Depends(get_current_user),
) -> List[bool]:
    if req.start + req.count - 1 > ETD_CHANNELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rentang channel melebihi batas 12",
        )

    try:
        regs = await svc().read_holding_registers(
            address=req.start - 1,
            count=req.count
        )
        return [v == ETD_OUTPUT_ON for v in regs]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )
