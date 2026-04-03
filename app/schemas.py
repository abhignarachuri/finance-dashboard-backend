from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import date



class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["viewer", "analyst", "admin"] = "viewer"


class UserUpdate(BaseModel):
    role: Optional[Literal["viewer", "analyst", "admin"]] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}  



class LoginRequest(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    token: str
    role: str



class FinanceRecordCreate(BaseModel):
    amount: float
    type: Literal["income", "expense"]  
    category: str
    date: date
    notes: Optional[str] = None         

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class FinanceRecordUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class FinanceRecordOut(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: date
    notes: Optional[str]

    model_config = {"from_attributes": True}  # allows reading directly from SQLAlchemy model objects
