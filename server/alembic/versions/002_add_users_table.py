"""Add users table and user_id to projects

Revision ID: 002
Revises: 001
Create Date: 2026-03-09

Creates:
- users: Registered user accounts
- Adds user_id FK to projects table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Users table ──────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── Add user_id to projects ──────────────────────────────
    # First create a default user so existing projects have a valid FK
    op.execute(
        "INSERT INTO users (email, full_name, hashed_password) "
        "VALUES ('admin@aitestengineer.com', 'Admin User', 'migrated-no-login')"
    )
    op.add_column("projects", sa.Column("user_id", sa.Integer(), nullable=True))
    op.execute("UPDATE projects SET user_id = 1")
    op.alter_column("projects", "user_id", nullable=False)
    op.create_foreign_key("fk_projects_user_id", "projects", "users", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_index("ix_projects_user_id", "projects", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_projects_user_id", table_name="projects")
    op.drop_constraint("fk_projects_user_id", "projects", type_="foreignkey")
    op.drop_column("projects", "user_id")
    op.drop_table("users")
