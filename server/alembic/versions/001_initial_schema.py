"""Initial schema — create all Phase 1 tables

Revision ID: 001
Revises: None
Create Date: 2026-03-02

Creates:
- projects: Top-level project container
- documents: Uploaded requirement files (FK → projects)
- test_cases: AI-generated test cases (FK → projects, documents)
- scripts: Automation scripts — Phase 2 (FK → test_cases)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Projects table ─────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ── Documents table ────────────────────────────────────────
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("file_type", sa.String(20), nullable=False),
        sa.Column("parsed_content", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), server_default="uploaded"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_documents_project_id", "documents", ["project_id"])

    # ── Test Cases table ───────────────────────────────────────
    op.create_table(
        "test_cases",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("test_case_id", sa.String(20), nullable=False),
        sa.Column("scenario", sa.Text(), nullable=False),
        sa.Column("preconditions", sa.Text(), nullable=True),
        sa.Column("test_steps", sa.JSON(), nullable=False),
        sa.Column("expected_result", sa.Text(), nullable=False),
        sa.Column("case_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), server_default="draft"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_test_cases_project_id", "test_cases", ["project_id"])
    op.create_index("ix_test_cases_document_id", "test_cases", ["document_id"])

    # ── Scripts table (Phase 2) ────────────────────────────────
    op.create_table(
        "scripts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("test_case_id", sa.Integer(), sa.ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("script_type", sa.String(20), nullable=False),
        sa.Column("language", sa.String(20), nullable=False),
        sa.Column("code_content", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), server_default="generated"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_scripts_test_case_id", "scripts", ["test_case_id"])


def downgrade() -> None:
    op.drop_table("scripts")
    op.drop_table("test_cases")
    op.drop_table("documents")
    op.drop_table("projects")
