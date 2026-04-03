# This file contains reusable building blocks (dependencies) that our routes plug into.
# FastAPI's Depends() system means these run automatically before the route handler does.

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth import get_token_data


def get_db():
    # Opens a fresh database session for each incoming request.
    # The yield means FastAPI will automatically close the session after the request finishes,
    # even if something goes wrong — no leaked connections.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: str = Header(...)):
    # Every protected route needs to know who is making the request.
    # The client sends their token in the Authorization header like: "Bearer abc123"
    # We strip the "Bearer " prefix and look up the token in our active_tokens store.
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ", 1)[1]
    data = get_token_data(token)
    if not data:
        # Token not found — either it was never issued or the server restarted
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return data  # returns {"user_id": int, "role": str}


def require_role(*roles: str):
    # A flexible role checker — you pass in which roles are allowed,
    # and it returns a dependency that enforces that rule.
    # For example: require_role("admin") only lets admins through.
    def checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in roles:
            # The user is logged in but doesn't have permission for this action
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
