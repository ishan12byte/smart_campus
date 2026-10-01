from app.database import SessionLocal, Base, engine
from app.models.role import Role
from app.models.department import Department
from app.models.user import User
from app.models.incident import Incident
from app.security import hash_password


def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Seed roles
        roles = [
        "STUDENT",
        "STAFF",
        "DEPARTMENT_HEAD",
        "SUPER_ADMIN"
    ]

        for role_name in roles:
            existing_role = db.query(Role).filter(
                Role.name == role_name
            ).first()

            if not existing_role:
                db.add(Role(name=role_name))

        # Seed departments
        departments = [
        ("EXAMINATION", "Examination"),
        ("ACADEMIC_ADMIN", "Academic Administration"),
        ("MAINTENANCE", "Maintenance"),
        ("SANITATION", "Sanitation"),
        ("IT", "Information Technology"),
        ("SECURITY", "Security"),
        ("ADMINISTRATION", "Administration")
    ]

        for department_code, department_name in departments:
            existing_department = db.query(Department).filter(
                Department.code == department_code
            ).first()

            if not existing_department:
                db.add(
                    Department(
                        code=department_code,
                        name=department_name
                    )
                )

        db.commit()

        # Seed initial users for development and demo testing
        student_role = db.query(Role).filter(Role.name == "STUDENT").first()
        staff_role = db.query(Role).filter(Role.name == "STAFF").first()
        admin_role = db.query(Role).filter(Role.name == "SUPER_ADMIN").first()
        admin_role_alias = db.query(Role).filter(Role.name == "ADMIN").first()
        if not admin_role_alias:
            db.add(Role(name="ADMIN"))
            db.commit()

        maint_dept = db.query(Department).filter(Department.code == "MAINTENANCE").first()
        admin_dept = db.query(Department).filter(Department.code == "ADMINISTRATION").first()
        acad_dept = db.query(Department).filter(Department.code == "ACADEMIC_ADMIN").first()

        default_users = [
            ("Student User", "student@campus.edu", "password123", student_role.id, acad_dept.id),
            ("Staff Member", "staff@campus.edu", "password123", staff_role.id, maint_dept.id),
            ("Campus Admin", "admin@campus.edu", "password123", admin_role.id, admin_dept.id),
        ]

        for name, email, raw_password, r_id, d_id in default_users:
            if not db.query(User).filter(User.email == email).first():
                db.add(
                    User(
                        name=name,
                        email=email,
                        password_hash=hash_password(raw_password),
                        role_id=r_id,
                        department_id=d_id,
                        is_active=True
                    )
                )

        db.commit()
        print("Seed data inserted successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()