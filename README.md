# Finance Dashboard API

A backend REST API for managing financial records with role-based access control. Built with FastAPI and SQLite.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Authentication](#authentication)
- [Roles & Permissions](#roles--permissions)
- [API Reference](#api-reference)
- [Validation Rules](#validation-rules)
- [How the System Works](#how-the-system-works)
- [Assumptions Made](#assumptions-made)
- [Tradeoffs Considered](#tradeoffs-considered)

---

## Overview

This API powers a finance dashboard where different types of users can view or manage financial data depending on their role.

It supports:
- Creating and managing users with different access levels
- Logging income and expense records
- Filtering records by category, type, and date range
- Retrieving aggregated summaries — total income, net balance, category breakdowns, and monthly trends

---

## Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Core language |
| FastAPI | 0.111.0 | Web framework and API routing |
| Uvicorn | 0.29.0 | ASGI server that runs FastAPI |
| SQLAlchemy | 2.0.30 | ORM — bridges Python models and SQLite |
| Pydantic | 2.7.1 | Request and response validation |
| SQLite | Built-in | Lightweight file-based database |

---

## Project Structure

```
finance_dashboard_backend/
├── app/
│   ├── main.py                 
│   ├── database.py           
│   ├── models.py               
│   ├── schemas.py              
│   ├── auth.py                
│   ├── crud.py                 
│   ├── dependencies.py        
│   ├── routes/
│   │   ├── users.py            
│   │   ├── finance.py         
│   │   └── dashboard.py      
│   └── services/
│       └── summary_service.py  
├── finance.db                  
├── requirements.txt            
├── test_all.py                 
└── .gitignore
```

---

## Setup & Installation

### Prerequisites

- Python 3.10
- pip



### Step 1 — Clone the repository

```bash
git clone https://github.com/your-username/finance_dashboard_backend.git
cd finance_dashboard_backend
```

---

### Step 2 — Create a virtual environment

A virtual environment keeps the project's dependencies isolated from the rest of your system.

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate



---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, SQLAlchemy, and Pydantic at the exact versions the project was built with.

---

### Step 4 — Start the server

```bash
python -m uvicorn app.main:app --reload
```

> If your terminal says `uvicorn: command not found`, use `python -m uvicorn app.main:app --reload` instead. This is common on Windows.

| Environment | Base URL |
|---|---|
| Local Development | `http://127.0.0.1:8000` |
| Production (example) | `https://your-domain.com` |

- The API will be live at `http://127.0.0.1:8000`
- Interactive Swagger docs are at `http://127.0.0.1:8000/docs`
- The `--reload` flag restarts the server automatically when you change a file

> `127.0.0.1` means your own machine (also called `localhost`). This URL only works while the server is running on your computer.

---

### Step 5 — Log in with the default admin account

On first startup, a default admin account is automatically created:

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |

Call `POST /users/login` with these credentials to get your token, then use that token in the `Authorization` header for all subsequent requests.

> Change this password before deploying to any public environment.

---

### Running the Tests

Make sure the server is running, then in a separate terminal:

```bash
python test_all.py
```

This runs 42 end-to-end tests covering all features authentication, user management, role access control, finance CRUD, validation, and dashboard summary.

---

## Authentication

This API uses **Bearer Token** authentication.

### How it works

1. Call `POST /users/login` with your username and password
2. You receive a token in the response
3. Send that token in the `Authorization` header on every subsequent request

```
Authorization: Bearer <your_token>
```

### Using Swagger UI

1. Open `http://127.0.0.1:8000/docs` in your browser
2. Call `POST /users/login` → click **Try it out** → enter credentials → click **Execute**
3. Copy the `token` value from the response
4. Click the 🔒 **Authorize** button at the top right of the Swagger page
5. Paste your token in the **Value** field — Swagger adds `Bearer` automatically
6. Click **Authorize** → **Close** — all subsequent requests will include your token

> Tokens live in server memory. They are cleared every time the server restarts. Log in again after each restart to get a fresh token.

---

## Roles & Permissions

There are three roles. Each one has a different level of access.

| Action | Viewer | Analyst | Admin |
|---|:---:|:---:|:---:|
| View dashboard summary | yes | yes | yes |
| View finance records (list) | no | yes | yes |
| View finance record (single) | no | yes | yes |
| Create finance records | no | no | yes |
| Update finance records | no | no | yes |
| Delete finance records | no | no | yes |
| Create users | no | no | yes |
| List all users | no | no | yes |
| Update user role or status | no | no | yes |

---

## API Reference

### Health Check

#### `GET /`

Confirms the server is running. No authentication required.

**Response**
```json
{
  "message": "Finance Dashboard API is running"
}
```

---

### Users

#### `POST /users/login`

Authenticates a user and returns a session token. No authentication required.

**Request Body**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**
```json
{
  "token": "a3f9c2d1...",
  "role": "admin"
}
```

| Status | Reason |
|---|---|
| 401 | Wrong username or password |
| 403 | Account is deactivated |

---

#### `POST /users/`

Creates a new user. Admin only.

**Request Body**
```json
{
  "username": "jane",
  "password": "securepass",
  "role": "analyst"
}
```

- `role` is optional and defaults to `viewer` if not provided
- Accepted role values: `viewer`, `analyst`, `admin`

**Response**
```json
{
  "id": 2,
  "username": "jane",
  "role": "analyst",
  "is_active": true
}
```

| Status | Reason |
|---|---|
| 400 | Username already exists |
| 403 | Caller is not an admin |
| 422 | Invalid role or missing required fields |

---

#### `GET /users/`

Returns a list of all users in the system. Admin only.

**Response**
```json
[
  {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "is_active": true
  },
  {
    "id": 2,
    "username": "jane",
    "role": "analyst",
    "is_active": true
  }
]
```

---

#### `PATCH /users/{user_id}`

Updates a user's role or active status. Admin only. All fields are optional — only include what you want to change.

**URL Parameter**
- `user_id` — the ID of the user to update

**Request Body**
```json
{
  "role": "viewer",
  "is_active": false
}
```

**Response** — returns the updated user object

| Status | Reason |
|---|---|
| 404 | User not found |
| 403 | Caller is not an admin |

---

### Finance Records

#### `POST /finance/`

Creates a new income or expense record. Admin only.

**Request Body**
```json
{
  "amount": 5000.00,
  "type": "income",
  "category": "salary",
  "date": "2024-01-15",
  "notes": "January salary"
}
```

- `type` must be `income` or `expense`
- `amount` must be greater than zero
- `notes` is optional
- `date` must be in `YYYY-MM-DD` format

**Response**
```json
{
  "id": 1,
  "amount": 5000.00,
  "type": "income",
  "category": "salary",
  "date": "2024-01-15",
  "notes": "January salary"
}
```

---

#### `GET /finance/`

Returns finance records. Analyst and admin only. All query parameters are optional — combine them to narrow results.

**Query Parameters**

| Parameter | Type | Description |
|---|---|---|
| `category` | string | Filter by category name (e.g. `salary`, `rent`) |
| `type` | string | Filter by `income` or `expense` |
| `start_date` | date | Include records on or after this date (`YYYY-MM-DD`) |
| `end_date` | date | Include records on or before this date (`YYYY-MM-DD`) |

**Example**
```
GET /finance/?type=expense&start_date=2024-01-01&end_date=2024-01-31
```

**Response** — list of matching records, sorted newest first

---

#### `GET /finance/{record_id}`

Returns a single finance record by its ID. Analyst and admin only.

**URL Parameter**
- `record_id` — the ID of the record

| Status | Reason |
|---|---|
| 404 | Record not found |

---

#### `PATCH /finance/{record_id}`

Updates one or more fields on an existing record. Admin only. All fields are optional.

**Request Body**
```json
{
  "amount": 5500.00,
  "category": "freelance"
}
```

**Response** — returns the updated record

| Status | Reason |
|---|---|
| 404 | Record not found |
| 422 | Invalid field value (e.g. negative amount) |

---

#### `DELETE /finance/{record_id}`

Permanently deletes a finance record. Admin only.

**Response**
```json
{
  "detail": "Record deleted"
}
```

| Status | Reason |
|---|---|
| 404 | Record not found |

---

### Dashboard

#### `GET /dashboard/summary`

Returns aggregated financial data. Available to all roles including viewer.

**Response**
```json
{
  "total_income": 9500.00,
  "total_expenses": 1500.00,
  "net_balance": 8000.00,
  "category_totals": {
    "salary": 9500.00,
    "rent": 1200.00,
    "groceries": 300.00
  },
  "recent_transactions": [
    {
      "id": 4,
      "amount": 4500.00,
      "type": "income",
      "category": "salary",
      "date": "2024-02-15",
      "notes": null
    }
  ],
  "monthly_trends": {
    "2024-01": { "income": 5000.00, "expense": 1200.00 },
    "2024-02": { "income": 4500.00, "expense": 300.00 }
  }
}
```

| Field | Description |
|---|---|
| `total_income` | Sum of all income records |
| `total_expenses` | Sum of all expense records |
| `net_balance` | `total_income` minus `total_expenses` |
| `category_totals` | Total amount grouped by category name |
| `recent_transactions` | The 5 most recent records by date |
| `monthly_trends` | Income and expense totals broken down per month |

---

## Validation Rules

All incoming data is validated automatically by Pydantic before it reaches the database. Invalid requests are rejected immediately with a `422` response and a clear error message.

| Rule | Detail |
|---|---|
| Amount must be positive | Zero and negative values are rejected |
| Type must be `income` or `expense` | Any other string is rejected |
| Role must be `viewer`, `analyst`, or `admin` | Any other string is rejected |
| Username must be unique | Duplicate usernames return `400` |
| Required fields must be present | Missing fields return `422` |
| Date must be in `YYYY-MM-DD` format | Invalid dates return `422` |

---

## How the System Works

### Request Lifecycle

Every request follows this path from start to finish:

```
Client sends request
        |
        v
FastAPI receives it and routes it (main.py)
        |
        v
Pydantic validates the request body shape and types (schemas.py)
        |
        v
Token is extracted from the Authorization header (dependencies.py)
        |
        v
Token is looked up in the in-memory store (auth.py)
        |
        v
User's role is checked against the route's requirement (dependencies.py)
        |
        v
Route handler executes (routes/)
        |
        v
CRUD function reads or writes to the database (crud.py)
        |
        v
SQLAlchemy translates Python objects to SQL (database.py)
        |
        v
SQLite executes the query (finance.db)
        |
        v
Result is serialized through Pydantic response schema (schemas.py)
        |
        v
JSON response returned to client
```

### Password Security

Passwords are never stored as plain text. When a user is created, the password is run through SHA-256 — a one-way hashing algorithm — and only the hash is saved to the database. During login, the typed password is hashed again and compared to the stored hash. The original password cannot be recovered from the database under any circumstances.

### Token System

When login succeeds, a cryptographically random 64-character hex string is generated using Python's `secrets` module. This token is stored in a server-side Python dictionary mapped to the user's ID and role. The client includes this token in every request header. The server looks it up to confirm identity and determine what the user is allowed to do.

### Role-Based Access Control

Every protected route has a role guard attached via FastAPI's `Depends()` system. The guard runs automatically before the route handler. If the user's role does not meet the requirement, the request is rejected with a `403 Access Denied` response before any database operation takes place.

---

## Assumptions Made

These are the decisions made about how the system should behave where the requirements left room for interpretation:

**1. Finance records are not tied to a specific user.**
All records exist at the system level. Any admin can create, edit, or delete any record. There is no concept of "my records" vs "other people's records."

**2. Only admins can create users.**
There is no self-registration. All accounts are provisioned by an admin. This keeps access tightly controlled in a finance context.

**3. Deactivating a user is preferred over deleting them.**
When an admin wants to remove someone's access, they set `is_active` to `false` rather than deleting the row. This preserves the user's history and makes the action reversible.

**4. Category is a free-text field.**
There is no predefined list of categories. Admins can use any string — `salary`, `rent`, `freelance`, etc. This keeps the system flexible without needing a separate category management layer.

**5. The dashboard summary covers all records across all time.**
There is no date filter on the summary endpoint. It always returns totals for the entire dataset. Filtering is available on the `/finance/` list endpoint instead.

**6. Tokens do not expire.**
A token remains valid until the server restarts or `revoke_token()` is called. There is no automatic expiry time. This was chosen for simplicity in a development context.

**7. The default admin password is hardcoded for first-run convenience.**
The `admin` / `admin123` account is seeded automatically so the system is usable immediately without any manual setup. It is expected to be changed before any real use.

---

## Tradeoffs Considered

These are the deliberate tradeoffs made in the design, along with the reasoning behind each choice:

---

**SQLite over PostgreSQL or MySQL**

SQLite was chosen because it requires zero configuration — no server to install, no connection string to manage, no credentials. The entire database is a single file. For a project of this scope and for local development, this is the right call. The tradeoff is that SQLite does not handle high concurrency well and is not suitable for a multi-server production deployment. Switching to PostgreSQL later would only require changing the `DATABASE_URL` in `database.py` — the rest of the code stays the same because SQLAlchemy abstracts the database layer.

---

**In-memory token store over JWT or a database-backed session**

Tokens are stored in a Python dictionary in server memory. This is simple, fast, and easy to reason about. The tradeoff is that all tokens are lost when the server restarts, which means every user has to log in again. It also means the system cannot scale horizontally — if you run two server instances, a token issued by one would not be recognised by the other. JWT (JSON Web Tokens) would solve both problems because the token itself contains the user's data and does not need to be looked up anywhere. JWT was not used here to keep the auth system simple and transparent.

---

**SHA-256 for password hashing over bcrypt**

SHA-256 is fast and built into Python's standard library with no extra dependencies. The tradeoff is that it is not designed for password hashing — it is too fast, which makes it easier to brute-force with a large list of guesses. bcrypt is the industry standard for passwords because it is intentionally slow and includes a salt automatically. For a production system, replacing `hashlib.sha256` with `bcrypt` or `passlib` would be the right move.

---

**No pagination on list endpoints**

`GET /finance/` and `GET /users/` return all matching records in a single response. This is fine for small datasets but would become a performance problem with thousands of records. Adding `limit` and `offset` query parameters to support pagination would be a straightforward improvement.

---

**No logout endpoint**

The `revoke_token()` function exists in `auth.py` but there is no route that calls it. This means tokens cannot be explicitly invalidated — they just disappear when the server restarts. Adding a `POST /users/logout` endpoint that calls `revoke_token()` would complete the auth lifecycle properly.

---

**Free-text category field over a managed category table**

Categories are plain strings rather than foreign keys to a separate `categories` table. This makes creating records simpler and avoids the need to pre-populate categories before using the system. The tradeoff is that there is no enforcement of consistent naming — `Salary`, `salary`, and `SALARY` would be treated as three different categories in the dashboard summary. A normalised category table would prevent this.
