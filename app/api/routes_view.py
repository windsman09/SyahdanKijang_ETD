from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import Channel

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request,"login.html")


@router.get("/etd8a12", response_class=HTMLResponse)
def etd_page(request: Request, session: Session = Depends(get_session)):
    channels = session.exec(
        select(Channel).order_by(Channel.channel)
    ).all()

    return templates.TemplateResponse(
            request,
        "etd8a12.html",
        {
            "channels": channels
        }
    )


@router.get("/channels")
def get_channels(session: Session = Depends(get_session)):
    return session.exec(
        select(Channel).order_by(Channel.channel)
    ).all()
