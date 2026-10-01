"""standardize role names

Revision ID: 7c07cc82383c
Revises: 784e10db15af
Create Date: 2026-09-20 23:02:12.017961

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c07cc82383c'
down_revision: Union[str, Sequence[str], None] = '784e10db15af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Standardize role names."""

    op.execute(
        sa.text(
            "UPDATE roles SET name = 'STUDENT' "
            "WHERE name = 'Student'"
        )
    )

    op.execute(
        sa.text(
            "UPDATE roles SET name = 'STAFF' "
            "WHERE name = 'Staff'"
        )
    )

    op.execute(
        sa.text(
            "UPDATE roles SET name = 'DEPARTMENT_HEAD' "
            "WHERE name = 'Department Head'"
        )
    )

    op.execute(
        sa.text(
            "UPDATE roles SET name = 'SUPER_ADMIN' "
            "WHERE name = 'Super Admin'"
        )
    )


def downgrade() -> None:
    """Restore original role names."""

    op.execute(
        sa.text(
            "UPDATE roles SET name = 'Student' "
            "WHERE name = 'STUDENT'"
        )
    )

    op.execute(
        sa.text(
            "UPDATE roles SET name = 'Staff' "
            "WHERE name = 'STAFF'"
        )
    )

    op.execute(
        sa.text(
            "UPDATE roles SET name = 'Department Head' "
            "WHERE name = 'DEPARTMENT_HEAD'"
        )
    )

    op.execute(
        sa.text(
            "UPDATE roles SET name = 'Super Admin' "
            "WHERE name = 'SUPER_ADMIN'"
        )
    )