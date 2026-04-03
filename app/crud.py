# CRUD stands for Create, Read, Update, Delete — the four basic database operations.
# This file is the only place in the app that directly talks to the database.
# Routes call these functions instead of writing raw queries themselves,
# which keeps things clean and easy to change later.

from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import hash_password
from datetime import date


# ── User Operations ───────────────────────────────────────────────────────────

def get_user_by_username(db: Session, username: str):
    # Used during login to find the user by their username.
    return db.query(models.User).filter(models.User.username == username).first()


def get_user(db: Session, user_id: int):
    # Used when we need to look up a specific user by their ID.
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_all_users(db: Session):
    # Returns every user in the system — only admins can call this.
    return db.query(models.User).all()


def create_user(db: Session, data: schemas.UserCreate):
    # Creates a new user. The password is hashed before saving —
    # we never store what the user actually typed.
    user = models.User(
        username=data.username,
        password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()       # saves the new user to the database permanently
    db.refresh(user)  # reloads the user from DB so we get the auto-generated ID
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


# ── Finance Record Operations ─────────────────────────────────────────────────

def create_record(db: Session, data: schemas.FinanceRecordCreate):
    # Saves a new income or expense entry to the database.
    # model_dump() converts the Pydantic schema into a plain dictionary
    # so we can unpack it directly into the model.
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
    # Fetches finance records with optional filters.
    # Filters are applied only if they were provided — unused filters are simply skipped.
    # Results are sorted newest first so the most recent transactions appear at the top.
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
    # Fetches a single finance record by its ID.
    return db.query(models.FinanceRecord).filter(models.FinanceRecord.id == record_id).first()


def update_record(db: Session, record_id: int, data: schemas.FinanceRecordUpdate):
    # Updates only the fields that were included in the request.
    # exclude_unset=True means fields the user didn't mention are left untouched.
    record = get_record(db, record_id)
    if not record:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, record_id: int):
    # Permanently removes a finance record from the database.
    # Returns False if the record didn't exist so the route can return a 404.
    record = get_record(db, record_id)
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True
