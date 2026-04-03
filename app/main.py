# This is the entry point of the entire application.
# FastAPI starts here, the database tables are created here,
# and all the route groups are registered here.

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.database import engine
from app import models
from app.routes import users, finance, dashboard

# This line looks at all our model classes (User, FinanceRecord) and creates
# the corresponding tables in finance.db if they don't already exist.
# It's safe to run every time — it won't overwrite existing data.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Dashboard API", version="1.0.0")


def custom_openapi():
    # This customises the auto-generated API docs (Swagger UI) to include
    # a "BearerAuth" security scheme. That's what adds the "Authorize" button
    # at the top of the docs page where you paste your token.
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
        }
    }
    # Apply the BearerAuth requirement to every single endpoint automatically,
    # so we don't have to add it manually to each route.
    for path in schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi

# Register all the route groups — each one handles a different part of the API.
app.include_router(users.router)
app.include_router(finance.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def seed_admin():
    # When the app starts for the first time, there are no users in the database.
    # This function automatically creates a default admin account so you can log in
    # right away without manually inserting a user.
    # If the admin already exists (e.g. on a restart), it does nothing.
    from app.database import SessionLocal
    from app import crud, schemas
    db = SessionLocal()
    try:
        if not crud.get_user_by_username(db, "admin"):
            crud.create_user(db, schemas.UserCreate(
                username="admin",
                password="admin123",
                role="admin"
            ))
    finally:
        db.close()


@app.get("/")
def root():
    # A simple health check endpoint — if this returns a response, the server is running.
    return {"message": "Finance Dashboard API is running"}
