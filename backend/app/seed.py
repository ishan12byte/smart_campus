from app.database import SessionLocal
from app.models.role import Role
from app.models.department import Department


def seed_data():
    db = SessionLocal()

    try:
        # Seed roles
        roles = [
            "Student",
            "Staff",
            "Department Head",
            "Super Admin"
        ]

        for role_name in roles:
            existing_role = db.query(Role).filter(
                Role.name == role_name
            ).first()

            if not existing_role:
                db.add(Role(name=role_name))

        # Seed departments
        departments = [
            "Examination",
            "Academic Administration",
            "Maintenance",
            "Sanitation",
            "IT",
            "Security",
            "Administration"
        ]

        for department_name in departments:
            existing_department = db.query(Department).filter(
                Department.name == department_name
            ).first()

            if not existing_department:
                db.add(
                    Department(
                        name=department_name
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