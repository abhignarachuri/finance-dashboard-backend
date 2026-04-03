# This file handles all finance record operations — the core data of the dashboard.
# All routes here are grouped under the /finance prefix.
# Reading is open to analysts and above; writing is restricted to admins only.

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app import crud, schemas
from app.dependencies import get_db, analyst_or_above, admin_only

router = APIRouter(prefix="/finance", tags=["Finance"])


@router.post("/", response_model=schemas.FinanceRecordOut, dependencies=[Depends(admin_only)])
def create_record(data: schemas.FinanceRecordCreate, db: Session = Depends(get_db)):
    # Only admins can add new finance records.
    # The data is validated by FinanceRecordCreate before it even reaches here —
    # so by this point we know the amount is positive and the type is valid.
    return crud.create_record(db, data)


@router.get("/", response_model=list[schemas.FinanceRecordOut], dependencies=[Depends(analyst_or_above)])
def list_records(
    category: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    # Returns finance records, with optional filters.
    # All filters are optional — if none are provided, all records are returned.
    # Analysts and admins can use this to explore the data.
    return crud.get_records(db, category=category, type=type, start_date=start_date, end_date=end_date)


@router.get("/{record_id}", response_model=schemas.FinanceRecordOut, dependencies=[Depends(analyst_or_above)])
def get_record(record_id: int, db: Session = Depends(get_db)):
    # Fetches a single finance record by its ID.
    # Useful when you need the full details of one specific transaction.
    record = crud.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.patch("/{record_id}", response_model=schemas.FinanceRecordOut, dependencies=[Depends(admin_only)])
def update_record(record_id: int, data: schemas.FinanceRecordUpdate, db: Session = Depends(get_db)):
    # Allows an admin to correct or update an existing finance record.
    # Only the fields included in the request body will be changed.
    record = crud.update_record(db, record_id, data)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.delete("/{record_id}", dependencies=[Depends(admin_only)])
def delete_record(record_id: int, db: Session = Depends(get_db)):
    # Permanently removes a finance record. Only admins can do this.
    # Returns a confirmation message so the client knows it worked.
    if not crud.delete_record(db, record_id):
        raise HTTPException(status_code=404, detail="Record not found")
    return {"detail": "Record deleted"}
