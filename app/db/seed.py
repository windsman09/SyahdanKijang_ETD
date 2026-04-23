# app/db/seed.py
import logging
from sqlmodel import Session, select
from app.db.models import User, Device, Channel
from app.core.security import get_password_hash

logger = logging.getLogger("app.seed")

def ensure_admin(session: Session):
    username = "admin"
    password = "admin123"
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        session.add(User(
            username=username,
            full_name="Administrator",
            hashed_password=get_password_hash(password),
            is_active=True,
        ))
        session.commit()
        logger.info("[seed] admin created")
    else:
        logger.info("[seed] admin already exists")

def ensure_devices(session: Session):
    # daftar kandidat device dari hasil scanmu (port 5000 open)
    specs = [
        ("Module-1", "10.21.240.2"),
        ("Module-2", "10.21.240.3"),
        ("Module-3", "10.21.240.4"),
        ("Module-4", "10.21.240.5"),
        ("Module-5", "10.21.240.7"),
    ]
    for name, ip in specs:
        dev = session.exec(select(Device).where(Device.name == name)).first()
        if not dev:
            dev = Device(
                name=name, ip=ip, port=5000, unit=1,
                io_type="coil", channels=12, timeout=5.0, retries=3,
                enabled=True
            )
            session.add(dev)
            logger.info(f"[seed] device created: {name} {ip}:5000")
    session.commit()

def ensure_device_channels(session: Session):
    devices = session.exec(select(Device).where(Device.enabled == True)).all()
    for d in devices:
        # contoh label default; bisa disesuaikan per device kalau perlu
        existing = {c.channel for c in session.exec(
            select(Channel).where(Channel.device_id == d.id)
        ).all()}
        for ch in range(1, d.channels + 1):
            if ch not in existing:
                session.add(Channel(device_id=d.id, channel=ch, name=f"{d.name} CH {ch}"))
        logger.info(f"[seed] channels ensured for {d.name}")
    session.commit()

def run_seed(session: Session):
    logger.info("[seed] start seeding data")
    ensure_admin(session)
    ensure_devices(session)
    ensure_device_channels(session)  # penting: per device
    logger.info("[seed] seeding finished")
