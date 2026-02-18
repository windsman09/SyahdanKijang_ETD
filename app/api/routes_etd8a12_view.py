from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router_etd_view = APIRouter(tags=["views"])
_templates = Jinja2Templates(directory="app/templates")

@router_etd_view.get("/etd8a12", response_class=HTMLResponse)
async def etd_page(request: Request):
    return _templates.TemplateResponse("etd8a12.html", {"request": request, "title": "ETD 8A12"})
