import os
import logging
from sqlmodel import Session, select
from app.db.models import User
from app.core.security import get_password_hash
from app.db.models import channels

logger = logging.getLogger("app.seed")

def ensure_admin(session: Session):
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")

    logger.info(
        f"[seed] ensuring admin '{username}' (len(chars)={len(password)}, len(bytes)={len(password.encode('utf-8'))})"
    )

    user = session.exec(select(User).where(User.username == username)).first()
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
channels=["Lampu K1B","K1B AC1","K1B AC2", "Lampu K1C","K1C AC1", "K1C AC2","Lampu K1D","K1D AC1","K1D AC2","Lampu K1E","K1E AC1","K1E AC2" ]
