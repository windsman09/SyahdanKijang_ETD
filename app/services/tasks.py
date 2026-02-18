
import asyncio
import logging
from app.core.config import settings
from app.services.modbus_client import ModbusService

logger = logging.getLogger("app.polling")


async def polling_loop(interval_sec: int = 5):
    if interval_sec <= 0:
        logger.info("Polling disabled")
        return

    svc = ModbusService(
        host=settings.etd_host,
        port=settings.etd_port,   # ✅ 5000
        unit_id=settings.etd_unit,
        timeout=2.0,
        retries=2,
    )

    logger.info(
        "Start polling ETD %s:%s every %ss",
        settings.etd_host,
        settings.etd_port,
        interval_sec,
    )

    while True:
        try:
            vals = await svc.read_holding_registers(address=0, count=12)
            logger.info("[poll] HR[0..11]=%s", vals)
        except asyncio.CancelledError:
            logger.info("Polling loop cancelled")
            break
        except Exception as e:
            logger.exception("Polling error: %s", e)

        await asyncio.sleep(interval_sec)
