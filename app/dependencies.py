from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth import get_token_data


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ", 1)[1]
    data = get_token_data(token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return data  


def require_role(*roles: str):
    def checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return checker


# These are named shortcuts so routes don't have to spell out the roles every time.
# viewer_or_above — can read basic data (all three roles)
# analyst_or_above — can read detailed finance records (analyst and admin)
# admin_only — can create, update, or delete anything (admin only)
viewer_or_above  = require_role("viewer", "analyst", "admin")
analyst_or_above = require_role("analyst", "admin")
admin_only       = require_role("admin")
