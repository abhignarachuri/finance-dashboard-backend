# This file sets up the connection to our SQLite database.
# SQLite is a lightweight database that stores everything in a single file (finance.db).
# We use SQLAlchemy as the bridge between Python and the database.

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# This is the path to our database file. The ./ means it will be created
# in the same folder where we run the app.
DATABASE_URL = "sqlite:///./finance.db"

# The engine is the actual connection to the database.
# check_same_thread=False is needed for SQLite when used with FastAPI,
# because FastAPI handles multiple requests across different threads.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal is a factory that creates new database sessions.
# Each request gets its own session — think of it like a temporary workspace
# where you read/write data, and then close it when done.
SessionLocal = sessionmaker(
    autocommit=False,  # we manually commit changes so nothing saves accidentally
    autoflush=False,   # we control when changes are pushed to the DB
    bind=engine
)

# Base is the parent class that all our database models (tables) will inherit from.
# When we define a model like class User(Base), SQLAlchemy knows to create a "users" table.
Base = declarative_base()
