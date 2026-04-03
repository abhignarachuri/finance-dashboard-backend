# This file serves the dashboard summary — a high-level overview of the financial data.
# Even viewers (the lowest role) can access this, since it's read-only and aggregated.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, viewer_or_above
from app.services.summary_service import get_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", dependencies=[Depends(viewer_or_above)])
def dashboard_summary(db: Session = Depends(get_db)):
    # Calls the summary service which crunches all the finance data and returns
    # totals, category breakdowns, recent transactions, and monthly trends.
    return get_summary(db)
