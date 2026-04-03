from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, viewer_or_above
from app.services.summary_service import get_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", dependencies=[Depends(viewer_or_above)])
def dashboard_summary(db: Session = Depends(get_db)):
    return get_summary(db)
