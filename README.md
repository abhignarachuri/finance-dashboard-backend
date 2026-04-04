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

## Approach
The backend is designed using a modular structure to separate responsibilities clearly.

* Routes handle incoming API requests
* Services contain business logic
* Models define database structure
* Schemas validate request and response data

The system follows role-based access control where permissions are enforced before executing protected operations.
Financial records are stored in a persistent database and summary endpoints calculate aggregated dashboard insights such as income, expenses, and balance.

## Installation
git clone <repo-url>
cd finance-dashboard
pip install -r requirements.txt

## Run Project
uvicorn main:app --reload

## Base URL-Local Environment
http://127.0.0.1:8000/docs

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
