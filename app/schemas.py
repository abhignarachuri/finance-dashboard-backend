# Schemas define the shape of data coming IN to the API and going OUT of it.
# They act as a contract — if the data doesn't match the expected shape, FastAPI
# automatically rejects the request with a clear error message.
# We use Pydantic for this, which also handles type validation automatically.

from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import date


# ── User Schemas ──────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    # What an admin must send when creating a new user.
    # Role defaults to "viewer" — the least privileged option — if not specified.
    username: str
    password: str
    role: Literal["viewer", "analyst", "admin"] = "viewer"


class UserUpdate(BaseModel):
    # What an admin can change about an existing user.
    # Both fields are optional — you can update just the role, just the status, or both.
    role: Optional[Literal["viewer", "analyst", "admin"]] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    # What gets sent back when user data is returned in a response.
    # Notice the password is NOT here — we never expose it, not even the hash.
    id: int
    username: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}  # allows reading directly from SQLAlchemy model objects


# ── Auth Schemas ──────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    # What the user sends when logging in.
    username: str
    password: str


class TokenOut(BaseModel):
    # What gets sent back after a successful login.
    # The token is what the user will include in all future requests.
    token: str
    role: str


# ── Finance Record Schemas ────────────────────────────────────────────────────

class FinanceRecordCreate(BaseModel):
    # What an admin must send when adding a new finance record.
    amount: float
    type: Literal["income", "expense"]  # only these two values are accepted
    category: str
    date: date
    notes: Optional[str] = None         # notes are optional

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        # A finance record with zero or negative amount doesn't make sense.
        # This validator catches that before it ever reaches the database.
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class FinanceRecordUpdate(BaseModel):
    # What an admin can send when editing an existing record.
    # Every field is optional — you only need to include what you want to change.
    amount: Optional[float] = None
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        # Same rule as above — if an amount is provided, it must be positive.
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class FinanceRecordOut(BaseModel):
    # What gets sent back when finance records are returned in a response.
    # This is a clean, safe version of the data — only what the client needs.
    id: int
    amount: float
    type: str
    category: str
    date: date
    notes: Optional[str]

    model_config = {"from_attributes": True}  # allows reading directly from SQLAlchemy model objects
