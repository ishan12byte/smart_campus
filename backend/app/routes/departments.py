from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.department import Department
from app.schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)
from app.auth import get_current_user


router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


@router.get(
    "",
    response_model=list[DepartmentResponse]
)
def get_departments(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Department)
        .order_by(Department.id)
        .all()
    )


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse
)
def get_department(
    department_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=201
)
def create_department(
    department_data: DepartmentCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_code = (
        db.query(Department)
        .filter(Department.code == department_data.code)
        .first()
    )

    if existing_code:
        raise HTTPException(
            status_code=400,
            detail="Department code already exists"
        )

    existing_name = (
        db.query(Department)
        .filter(Department.name == department_data.name)
        .first()
    )

    if existing_name:
        raise HTTPException(
            status_code=400,
            detail="Department name already exists"
        )

    new_department = Department(
        code=department_data.code,
        name=department_data.name,
        description=department_data.description
    )

    db.add(new_department)
    db.commit()
    db.refresh(new_department)

    return new_department


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse
)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    if department_data.code is not None:
        department.code = department_data.code

    if department_data.name is not None:
        department.name = department_data.name

    if department_data.description is not None:
        department.description = department_data.description

    if department_data.is_active is not None:
        department.is_active = department_data.is_active

    db.commit()
    db.refresh(department)

    return department