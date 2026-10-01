from fastapi import FastAPI

from app.database import Base, engine
from app.models.role import Role
from app.models.department import Department
from app.models.user import User
from app.models.incident import Incident


from app.auth import router as auth_router
from app.rbac import require_roles


from app.routes.incidents import router as incidents_router
from app.routes.departments import router as departments_router
from app.routes.roles import router as roles_router
from app.routes.users import router as users_router
from app.routes.admin import router as admin_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Smart Campus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(incidents_router)

app.include_router(departments_router)


app.include_router(roles_router)

app.include_router(users_router)

app.include_router(admin_router)

@app.get("/")
def root():
    return {
        "message": "Smart Campus API is running"
    }