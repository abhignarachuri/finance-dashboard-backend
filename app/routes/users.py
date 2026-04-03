# This file handles everything related to users — logging in and managing accounts.
# All routes here are grouped under the /users prefix.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.auth import verify_password, create_token
from app.dependencies import get_db, admin_only

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/login", response_model=schemas.TokenOut)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    # The entry point for any user wanting to access the dashboard.
    # We check if the username exists, then verify the password.
    # If everything checks out and the account is active, we issue a token.
    # That token is what the user will attach to every future request.
    user = crud.get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        # The account exists but an admin has disabled it
        raise HTTPException(status_code=403, detail="Account is deactivated")
    token = create_token(user.id, user.role)
    return {"token": token, "role": user.role}


@router.post("/", response_model=schemas.UserOut, dependencies=[Depends(admin_only)])
def create_user(data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Only admins can create new users.
    # We check for duplicate usernames first to avoid a database error later.
    if crud.get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud.create_user(db, data)


@router.get("/", response_model=list[schemas.UserOut], dependencies=[Depends(admin_only)])
def list_users(db: Session = Depends(get_db)):
    # Returns a list of all users in the system.
    # Only admins can see this — useful for managing who has access.
    return crud.get_all_users(db)


@router.patch("/{user_id}", response_model=schemas.UserOut, dependencies=[Depends(admin_only)])
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db)):
    # Allows an admin to change a user's role or deactivate their account.
    # Deactivating is safer than deleting — the user's history is preserved.
    user = crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
