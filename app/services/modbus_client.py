import asyncio
import logging
from typing import Optional, List

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

logger = logging.getLogger("app.modbus")


class ModbusService:
    def __init__(
        self,
        host: str,
        port: int = 5000,
        slave_id: int = 1,
        timeout: float = 8.0,
        retries: int = 3,
    ):
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.timeout = timeout
        self.retries = retries
        self.client: Optional[AsyncModbusTcpClient] = None

    async def connect(self):
        if self.client and self.client.connected:
            return

        self.client = AsyncModbusTcpClient(
            self.host,
            port=self.port,
            timeout=self.timeout,
        )

        await self.client.connect()

        if not self.client.connected:
            raise ConnectionError(f"Cannot connect to {self.host}:{self.port}")

        logger.info(f"Connected to Modbus {self.host}:{self.port}")

    async def close(self):
        if self.client is not None:
            try:
                await self.client.close()
            except Exception:
                pass

        self.client = None

    async def _with_retry(self, func):
        last_exc = None

        for attempt in range(self.retries):
            try:
                await self.connect()

                result = await asyncio.wait_for(
                    func(),
                    timeout=self.timeout
                )

                if hasattr(result, "isError") and result.isError():
                    raise ModbusException(str(result))

                return result

            except (asyncio.TimeoutError, ModbusException, OSError) as e:
                last_exc = e
                logger.warning(f"Modbus attempt {attempt+1} failed: {e}")

                await asyncio.sleep(0.5)

                if self.client:
                    try:
                        await self.client.close()
                    except Exception:
                        pass

                    self.client = None

        raise last_exc

    async def read_holding_registers(self, address: int) -> List[int]:
        rr = await self._with_retry(
            lambda: self.client.read_holding_registers(address)
        )

        return list(rr.registers)

    async def write_single_register(self, address: int, value: int) -> bool:
        if not (0 <= value <= 65535):
            raise ValueError("Register value must be 0..65535")

        await self._with_retry(
            lambda: self.client.write_register(
                address,
                value
            )
        )

        return True
