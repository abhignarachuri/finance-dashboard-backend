# Finance Dashboard Backend
Backend system for managing financial records, user roles, access permissions, and dashboard summaries.

## Features
- User and role management
- Financial record CRUD operations
- Dashboard summary APIs
- Role-based access control
- Validation and error handling
- Persistent storage using SQLite

## Tech Stack
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## Installation
git clone <repo-url>
cd finance-dashboard
pip install -r requirements.txt

## Run Project
uvicorn main:app --reload

## Base URL
http://localhost:8000

## Main Endpoints
/users
/records
/dashboard

## Roles
- Viewer → Read only
- Analyst → Read records + summaries
- Admin → Full management access

## Database
SQLite used for local persistence.

## Future Improvements
- JWT Authentication
- Pagination
- Audit logging
- PostgreSQL migration
