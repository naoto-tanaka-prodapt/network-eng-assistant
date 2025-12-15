from fastapi import APIRouter, Depends, HTTPException
from libs.db import get_session
from models import History

router = APIRouter()

@router.get("/api/history")
async def get_history(db=Depends(get_session)):
    histories = db.query(History).all()
    return histories


@router.get("/api/history/{history_id}")
async def get_history_detail(history_id: int, db=Depends(get_session)):
    history = db.get(History, history_id)
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    return history
