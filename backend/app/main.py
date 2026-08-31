from fastapi import FastAPI

from app.database import Base, engine
from app.models.role import Role
from app.models.department import Department
from app.models.user import User
from app.models.incident import Incident

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "Smart Campus API is running"
    }