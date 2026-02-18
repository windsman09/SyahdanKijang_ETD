from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import Channel
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/etd8a12")
def etd_page(request: Request):
    return templates.TemplateResponse("etd8a12.html", {"request": request})

@router.get("/channels")
def get_channels(session: Session = Depends(get_session)):
    return session.exec(select(Channel).order_by(Channel.index)).all()
