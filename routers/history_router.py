from fastapi import APIRouter, Depends
from libs.db import get_session
from models import History

router = APIRouter()

@router.get("/api/history")
async def get_history(db=Depends(get_session)):
    histories = db.query(History).all()
    return histories