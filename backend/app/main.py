from fastapi import FastAPI

from app.database import Base, engine
from app.models.role import Role
from app.models.department import Department
from app.models.user import User
from app.models.incident import Incident
from app.models.user import User
from app.auth import router as auth_router
from app.incidents import router as incidents_router


app = FastAPI()

Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(incidents_router)




@app.get("/")
def root():
    return {
        "message": "Smart Campus API is running"
    }