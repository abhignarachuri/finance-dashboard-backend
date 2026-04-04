# Finance Dashboard API

A backend REST API for managing financial records with role-based access control. Built with FastAPI and SQLite.

---

## What this project does

This API powers a finance dashboard where different users can view or manage financial data depending on their role. Some users can only read summaries. Others can dig into records. Admins have full control.

It handles user management, financial record tracking, role-based access, and a dashboard that gives you totals, trends, and breakdowns — all out of the box.

---

## Tech stack

- Python 3.10+
- FastAPI 0.111.0
- Uvicorn 0.29.0
- SQLAlchemy 2.0.30
- Pydantic 2.7.1
- SQLite (built-in, no setup needed)

---

## Project structure

```
finance_dashboard_backend/
├── app/
│   ├── main.py               # starts the app, registers routes, seeds admin user
│   ├── database.py           # database connection and session setup
│   ├── models.py             # database table definitions
│   ├── schemas.py            # request and response validation
│   ├── auth.py               # password hashing and token management
│   ├── crud.py               # all database read/write logic
│   ├── dependencies.py       # auth checks and role guards
│   ├── routes/
│   │   ├── users.py          # user endpoints
│   │   ├── finance.py        # finance record endpoints
│   │   └── dashboard.py      # dashboard summary endpoint
│   └── services/
│       └── summary_service.py  # dashboard aggregation logic
├── finance.db                # SQLite database (auto-created on first run)
└── requirements.txt
```

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/finance_dashboard_backend.git
cd finance_dashboard_backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the server

```bash
python -m uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`
Swagger docs are at `http://127.0.0.1:8000/docs`

> `127.0.0.1` is your own machine. The server only runs while this command is active. The `--reload` flag automatically restarts it when you save a file.

### 5. Log in

A default admin account is created automatically on first startup. Use it to get a token and start making requests.

> Change this password before putting this anywhere public.

---

## Authentication

This API uses Bearer Token auth.

1. Call `POST /users/login` with your username and password
2. Copy the `token` from the response
3. Include it in every request header like this:

```
Authorization: Bearer <your_token>
```

### In Swagger

1. Open `http://127.0.0.1:8000/docs`
2. Call `POST /users/login` → Try it out → enter credentials → Execute
3. Copy the token from the response
4. Click the **Authorize** button at the top right
5. Paste your token — Swagger adds `Bearer` automatically
6. Click Authorize → Close

Tokens are stored in memory and cleared on every server restart. Just log in again to get a new one.

---

## Roles

Three roles, each with different access:

| Action | Viewer | Analyst | Admin |
|---|:---:|:---:|:---:|
| View dashboard summary | yes | yes | yes |
| View finance records | no | yes | yes |
| Create / update / delete records | no | no | yes |
| Create / list / update users | no | no | yes |

---

## API reference

### Health check

```
GET /
```
No auth needed. Just confirms the server is up.

---

### Users

#### Login
```
POST /users/login
```
```json
{ "username": "admin", "password": "admin123" }
```
Returns a token and the user's role. No auth required.

---

#### Create a user
```
POST /users/
```
Admin only.
```json
{
  "username": "jane",
  "password": "securepass",
  "role": "analyst"
}
```
`role` defaults to `viewer` if not provided. Accepted values: `viewer`, `analyst`, `admin`.

---

#### List all users
```
GET /users/
```
Admin only. Returns all users.

---

#### Update a user
```
PATCH /users/{user_id}
```
Admin only. Update role, active status, or both. All fields optional.
```json
{ "role": "viewer", "is_active": false }
```

---

### Finance records

#### Create a record
```
POST /finance/
```
Admin only.
```json
{
  "amount": 5000.00,
  "type": "income",
  "category": "salary",
  "date": "2024-01-15",
  "notes": "January salary"
}
```
`notes` is optional. `type` must be `income` or `expense`. `amount` must be greater than zero.

---

#### List records
```
GET /finance/
```
Analyst and admin only. All filters are optional:

| Param | Description |
|---|---|
| `category` | filter by category name |
| `type` | `income` or `expense` |
| `start_date` | on or after this date (YYYY-MM-DD) |
| `end_date` | on or before this date (YYYY-MM-DD) |

Results are sorted newest first.

---

#### Get a single record
```
GET /finance/{record_id}
```
Analyst and admin only.

---

#### Update a record
```
PATCH /finance/{record_id}
```
Admin only. All fields optional.

---

#### Delete a record
```
DELETE /finance/{record_id}
```
Admin only. Permanently removes the record.

---

### Dashboard

```
GET /dashboard/summary
```
Available to all roles. Returns:

| Field | What it is |
|---|---|
| `total_income` | sum of all income records |
| `total_expenses` | sum of all expense records |
| `net_balance` | income minus expenses |
| `category_totals` | total per category |
| `recent_transactions` | the 5 most recent records |
| `monthly_trends` | income and expense per month |

---

## Validation

Pydantic validates every request before it touches the database. Bad input gets a `422` with a clear message.

- Amount must be greater than zero
- Type must be `income` or `expense`
- Role must be `viewer`, `analyst`, or `admin`
- Usernames must be unique
- Dates must be in `YYYY-MM-DD` format

---

## How it works under the hood

Every request goes through this path:

```
Request comes in
  → FastAPI routes it
  → Pydantic validates the body
  → Token is pulled from the Authorization header
  → Token is looked up in memory to identify the user
  → Role is checked against what the route requires
  → Route handler runs
  → CRUD function reads or writes to the database
  → SQLAlchemy translates it to SQL
  → SQLite executes it
  → Response is shaped by Pydantic and returned as JSON
```

Passwords are hashed with SHA-256 before being stored. The original password is never saved anywhere. On login, the input is hashed and compared to the stored hash.

Tokens are random 64-character hex strings generated with Python's `secrets` module. They live in a server-side dictionary until the server restarts.

Role guards run automatically via FastAPI's `Depends()` system before any route logic executes. If the role doesn't match, the request is rejected with a `403` immediately.

---

## Design decisions worth knowing

**Finance records aren't tied to a user.** Records exist at the system level. Any admin can create, edit, or delete any record.

**No self-registration.** Only admins can create accounts. This keeps access controlled in a finance context.

**Deactivation over deletion.** Setting `is_active` to `false` removes access without losing the user's history. It's reversible.

**Categories are free text.** No predefined list. Admins can use any string. The tradeoff is that `Salary` and `salary` are treated as different categories in the dashboard.

**The dashboard has no date filter.** It always covers all records. Use the `/finance/` filters if you need a specific range.

**Tokens don't expire.** They're cleared on server restart. Simple enough for development, but you'd want proper expiry in production.

**SQLite over PostgreSQL.** Zero config, single file, works immediately. Not suitable for high concurrency or multi-server deployments. Switching to PostgreSQL later only requires changing `DATABASE_URL` in `database.py`.

**SHA-256 over bcrypt.** Built into Python, no extra dependencies. The tradeoff is it's faster than ideal for password hashing. For production, swap it out for `bcrypt` or `passlib`.

**No pagination.** List endpoints return everything. Fine for small datasets, but you'd want `limit` and `offset` params before scaling up.

**No logout endpoint.** `revoke_token()` exists in `auth.py` but there's no route wired to it yet. Tokens just disappear on restart.
