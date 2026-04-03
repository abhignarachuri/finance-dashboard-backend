from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.database import engine
from app import models
from app.routes import users, finance, dashboard

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Dashboard API", version="1.0.0")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
        }
    }

    for path in schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi

app.include_router(users.router)
app.include_router(finance.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def seed_admin():
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
