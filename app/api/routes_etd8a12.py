from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

from app.core.security import get_current_user
from app.services.modbus_client import ModbusService

router = APIRouter(prefix="/etd8a12", tags=["etd8a12"])

# =========================
# Konfigurasi ETD / Modbus
# =========================
ETD_HOST = "10.21.240.2"   # pastikan IP benar
ETD_PORT = 5000            # pastikan port benar (banyak device Modbus TCP defaultnya 502)
ETD_UNIT = 1

ETD_CHANNELS = 12  # CH1..CH12 → address 0..11 (cek mapping perangkat)

# Banyak perangkat memakai FC=5 (write single coil) untuk ON/OFF.
# Nilai berikut hanya berlaku jika perangkat memang butuh write register dengan value spesifik.
ETD_OUTPUT_ON  = 0x0100
ETD_OUTPUT_OFF = 0x0200

# =========================
# Modbus Service (singleton)
# =========================
_modbus_service = ModbusService(
    host=ETD_HOST,
    port=ETD_PORT,
    slave_id=ETD_UNIT,
    timeout=5.0,   # perpanjang sedikit untuk jaringan industri
    retries=3,
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
# Channels (untuk label UI)
# =========================
@router.get("/channels")
async def get_channels(user=Depends(get_current_user)):
    """
    Mengembalikan daftar nama channel (sementara default CH 1..CH 12).
    Jika nanti ada tabel Channel di DB, ambil dari sana.
    """
    return [{"index": i, "name": f"CH {i}"} for i in range(1, ETD_CHANNELS + 1)]

# =========================
# Outputs (status & control)
# =========================
@router.get("/outputs", response_model=List[bool])
async def get_all_outputs(user=Depends(get_current_user)) -> List[bool]:
    try:
        # --- PILIH SALAH SATU SESUAI PERANGKAT ---

        # 1) Jika status output disimpan di HOLDING REGISTER:
        regs = await svc().read_holding_registers(address=0, count=ETD_CHANNELS)
        # Mapping ke bool: sesuaikan (0/1 atau 0x0100/0x0200). Contoh generik:
        states = [(v in (1, ETD_OUTPUT_ON, True)) for v in regs]
        return states

        # 2) Jika ternyata status output ada di COIL:
        # coils = await svc().read_coils(address=0, count=ETD_CHANNELS)
        # return [bool(v) for v in coils]

    except Exception as e:
        # Tambahkan detail supaya terlihat di UI/log
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"modbus read failed host={ETD_HOST} port={ETD_PORT} unit={ETD_UNIT}: {e!s}",
        )

@router.get("/outputs/{channel}", response_model=bool)
async def get_output(channel: int, user=Depends(get_current_user)) -> bool:
    if not (1 <= channel <= ETD_CHANNELS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"channel harus 1..{ETD_CHANNELS}",
        )

    try:
        # HOLDING:
        regs = await svc().read_holding_registers(address=channel - 1, count=1)
        v = regs[0]
        return (v in (1, ETD_OUTPUT_ON, True))

        # COIL (alternatif):
        # coils = await svc().read_coils(address=channel - 1, count=1)
        # return bool(coils[0])

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"modbus read(ch={channel}) failed host={ETD_HOST} port={ETD_PORT} unit={ETD_UNIT}: {e!s}",
        )

@router.post("/outputs/set")
async def set_output(req: ChannelWrite, user=Depends(get_current_user)) -> dict:
    addr = req.channel - 1

    try:
        # --- PILIH SESUAI PERANGKAT ---

        # 1) Jika ON/OFF dilakukan lewat write SINGLE REGISTER:
        value = ETD_OUTPUT_ON if req.on else ETD_OUTPUT_OFF
        ok = await svc().write_single_register(address=addr, value=value)

        # 2) Jika ON/OFF seharusnya lewat write SINGLE COIL (FC=5):
        # ok = await svc().write_single_coil(address=addr, value=req.on)

        return {"ok": bool(ok), "channel": req.channel, "requested_on": req.on}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"modbus write(ch={req.channel}) failed host={ETD_HOST} port={ETD_PORT} unit={ETD_UNIT}: {e!s}",
        )

@router.post("/outputs/read-range", response_model=List[bool])
async def read_range(req: ChannelRange, user=Depends(get_current_user)) -> List[bool]:
    if req.start + req.count - 1 > ETD_CHANNELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rentang channel melebihi batas {ETD_CHANNELS}",
        )

    try:
        # HOLDING:
        regs = await svc().read_holding_registers(address=req.start - 1, count=req.count)
        return [(v in (1, ETD_OUTPUT_ON, True)) for v in regs]

        # COIL (alternatif):
        # coils = await svc().read_coils(address=req.start - 1, count=req.count)
        # return [bool(v) for v in coils]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"modbus read-range(start={req.start}, count={req.count}) failed host={ETD_HOST} port={ETD_PORT} unit={ETD_UNIT}: {e!s}",
        )
