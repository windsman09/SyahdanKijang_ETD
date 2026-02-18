from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from app.db.session import get_session
from app.db.models import Item
from app.core.security import get_current_user

router = APIRouter(prefix="/items", tags=["items"])

class ItemIn(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)

@router.get("/")
async def list_items(session: Session = Depends(get_session), user=Depends(get_current_user)):
    return session.exec(select(Item)).all()

@router.post("/", response_model=Item)
async def create_item(data: ItemIn, session: Session = Depends(get_session), user=Depends(get_current_user)):
    row = Item(**data.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
