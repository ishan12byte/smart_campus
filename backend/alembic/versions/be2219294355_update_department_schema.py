"""update department schema

Revision ID: be2219294355
Revises: 7c07cc82383c
Create Date: 2026-09-26 09:40:50.227942

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "be2219294355"
down_revision: Union[str, Sequence[str], None] = "7c07cc82383c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # 1. Add code temporarily as nullable.
    op.add_column(
        "departments",
        sa.Column(
            "code",
            sa.String(length=50),
            nullable=True
        )
    )

    # 2. Add timestamps.
    op.add_column(
        "departments",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        )
    )

    op.add_column(
        "departments",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        )
    )

    # 3. Give existing departments codes.
    op.execute(
        """
        UPDATE departments
        SET code = CASE name
            WHEN 'Examination' THEN 'EXAMINATION'
            WHEN 'Academic Administration' THEN 'ACADEMIC_ADMIN'
            WHEN 'Maintenance' THEN 'MAINTENANCE'
            WHEN 'Sanitation' THEN 'SANITATION'
            WHEN 'IT' THEN 'IT'
            WHEN 'Security' THEN 'SECURITY'
            WHEN 'Administration' THEN 'ADMINISTRATION'
        END
        """
    )

    # 4. Make code required.
    op.alter_column(
        "departments",
        "code",
        nullable=False
    )

    # 5. Remove unique constraint from name.
    op.drop_constraint(
        "departments_name_key",
        "departments",
        type_="unique"
    )

    # 6. Make code unique.
    op.create_unique_constraint(
        "uq_departments_code",
        "departments",
        ["code"]
    )


def downgrade() -> None:

    op.drop_constraint(
        "uq_departments_code",
        "departments",
        type_="unique"
    )

    op.create_unique_constraint(
        "departments_name_key",
        "departments",
        ["name"]
    )

    op.drop_column(
        "departments",
        "updated_at"
    )

    op.drop_column(
        "departments",
        "created_at"
    )

    op.drop_column(
        "departments",
        "code"
    )