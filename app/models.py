# This file defines the shape of our database tables.
# Each class here becomes a table in finance.db.
# SQLAlchemy reads these classes and creates the actual tables when the app starts.

from sqlalchemy import Column, Integer, String, Boolean, Float, Date
from app.database import Base


# The User table stores everyone who can log into the dashboard.
# Each user has a role that controls what they're allowed to do.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # unique ID for each user
    username = Column(String, unique=True, index=True)  # no two users can share a username
    password = Column(String)                           # stored as a SHA-256 hash, never plain text
    role = Column(String)                               # "viewer", "analyst", or "admin"
    is_active = Column(Boolean, default=True)           # admins can deactivate users without deleting them


# The FinanceRecord table stores every income or expense entry.
# This is the core data that the dashboard is built around.
class FinanceRecord(Base):
    __tablename__ = "finance_records"

    id = Column(Integer, primary_key=True, index=True)  # unique ID for each record
    amount = Column(Float)                               # how much money (always positive)
    type = Column(String)                                # either "income" or "expense"
    category = Column(String)                            # e.g. "salary", "rent", "groceries"
    date = Column(Date)                                  # when this transaction happened
    notes = Column(String)                               # optional extra details about the transaction
