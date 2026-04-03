from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import hash_password
from datetime import date



def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_all_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, data: schemas.UserCreate):
    user = models.User(
        username=data.username,
        password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()       
    db.refresh(user)  
    return user


def update_user(db: Session, user_id: int, data: schemas.UserUpdate):
    # Allows an admin to change a user's role or activate/deactivate their account.
    # Only updates the fields that were actually provided in the request.
    user = get_user(db, user_id)
    if not user:
        return None
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    return user



def create_record(db: Session, data: schemas.FinanceRecordCreate):
    record = models.FinanceRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_records(
    db: Session,
    category: str | None = None,
    type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    q = db.query(models.FinanceRecord)
    if category:
        q = q.filter(models.FinanceRecord.category == category)
    if type:
        q = q.filter(models.FinanceRecord.type == type)
    if start_date:
        q = q.filter(models.FinanceRecord.date >= start_date)
    if end_date:
        q = q.filter(models.FinanceRecord.date <= end_date)
    return q.order_by(models.FinanceRecord.date.desc()).all()


def get_record(db: Session, record_id: int):
    return db.query(models.FinanceRecord).filter(models.FinanceRecord.id == record_id).first()


def update_record(db: Session, record_id: int, data: schemas.FinanceRecordUpdate):
    record = get_record(db, record_id)
    if not record:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, record_id: int):
    # Returns False if the record didn't exist so the route can return a 404.
    record = get_record(db, record_id)
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True
