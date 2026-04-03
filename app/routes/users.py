from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.auth import verify_password, create_token
from app.dependencies import get_db, admin_only

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/login", response_model=schemas.TokenOut)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    token = create_token(user.id, user.role)
    return {"token": token, "role": user.role}


@router.post("/", response_model=schemas.UserOut, dependencies=[Depends(admin_only)])
def create_user(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud.create_user(db, data)


@router.get("/", response_model=list[schemas.UserOut], dependencies=[Depends(admin_only)])
def list_users(db: Session = Depends(get_db)):
    return crud.get_all_users(db)


@router.patch("/{user_id}", response_model=schemas.UserOut, dependencies=[Depends(admin_only)])
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db)):
    # Allows an admin to change a user's role or deactivate their account.
    # Deactivating is safer than deleting — the user's history is preserved.
    user = crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
