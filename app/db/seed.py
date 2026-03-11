import os
import logging
from sqlmodel import Session, select
from app.db.models import User, Channel
from app.core.security import get_password_hash

logger = logging.getLogger("app.seed")


def ensure_admin(session: Session):
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")

    logger.info(
        f"[seed] ensuring admin '{username}' (len(chars)={len(password)}, len(bytes)={len(password.encode('utf-8'))})"
    )

    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    if not user:
        admin = User(
            username=username,
            full_name="Administrator",
            hashed_password=get_password_hash(password),
            is_active=True,
        )
        session.add(admin)
        session.commit()
        logger.info("[seed] admin created")
    else:
        logger.info("[seed] admin already exists")


def ensure_channels(session: Session):
    channels = [
        (1, "Lampu K1B"),
        (2, "K1B AC1"),
        (3, "K1B AC2"),
        (4, "Lampu K1C"),
        (5, "K1C AC1"),
        (6, "K1C AC2"),
        (7, "Lampu K1D"),
        (8, "K1D AC1"),
        (9, "K1D AC2"),
        (10, "Lampu K1E"),
        (11, "K1E AC1"),
        (12, "K1E AC2"),
    ]

    for ch_num, name in channels:
        existing = session.exec(
            select(Channel).where(Channel.channel == ch_num)
        ).first()

        if not existing:
            channel = Channel(
                channel=ch_num,
                name=name
            )
            session.add(channel)
            logger.info(f"[seed] channel created: {name}")
        else:
            logger.info(f"[seed] channel exists: {name}")

    session.commit()


def run_seed(session: Session):
    logger.info("[seed] start seeding data")

    ensure_admin(session)
    ensure_channels(session)

    logger.info("[seed] seeding finished")
