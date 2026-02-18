import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, List

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

logger = logging.getLogger("app.modbus")

class ModbusService:
    def __init__(self, host: str, port: int = 502, unit_id: int = 1, timeout: float = 2.0, retries: int = 2):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self.retries = retries

    @asynccontextmanager
    async def _client(self):
        client = AsyncModbusTcpClient(self.host, port=self.port, timeout=self.timeout)
        try:
            await client.connect()
            if not client.connected:
                raise ConnectionError(f"Cannot connect to {self.host}:{self.port}")
            yield client
        finally:
            try:
                await client.close()
            except Exception:
                pass

    async def _with_retry(self, coro_factory, expect_attr: str = ""):
        last_exc: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            try:
                result = await asyncio.wait_for(coro_factory(), timeout=self.timeout + 0.5)
                if hasattr(result, "isError") and result.isError():
                    raise ModbusException(str(result))
                if expect_attr and not hasattr(result, expect_attr):
                    raise ModbusException(f"Unexpected response (no {expect_attr})")
                return result
            except (asyncio.TimeoutError, ModbusException, OSError) as e:
                last_exc = e
                logger.warning(f"Modbus attempt {attempt+1} failed: {e}")
                await asyncio.sleep(0.2)
        assert last_exc is not None
        raise last_exc

    async def read_holding_registers(self, address: int, count: int = 1) -> List[int]:
        async with self._client() as client:
            rr = await self._with_retry(lambda: client.read_holding_registers(address, count, slave=self.unit_id), expect_attr="registers")
            return list(rr.registers)

    async def write_single_register(self, address: int, value: int) -> bool:
        if not (0 <= value <= 0xFFFF):
            raise ValueError("Register value must be 0..65535 (16-bit)")
        async with self._client() as client:
            await self._with_retry(lambda: client.write_register(address, value, slave=self.unit_id))
            return True
