
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Register all database models.
import app.models

# API routers
from app.auth import router as auth_router
from app.routes.incidents import router as incidents_router
from app.routes.departments import router as departments_router
from app.routes.roles import router as roles_router
from app.routes.users import router as users_router
from app.routes.admin import router as admin_router


app = FastAPI(
    title="Smart Campus API",
    description="Backend APIs for the Smart Campus application",
    version="1.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REGISTER API ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(incidents_router)
app.include_router(departments_router)
app.include_router(roles_router)
app.include_router(users_router)
app.include_router(admin_router)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Smart Campus API is running"
    }
