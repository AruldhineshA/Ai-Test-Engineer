"""
Test Case Database Model
=========================
Stores AI-generated test cases.

LEARN: JSON column type
- test_steps is stored as JSON in PostgreSQL
- PostgreSQL has native JSON support (very efficient)
- SQLAlchemy's JSON type maps directly to it
"""

from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class TestCase(Base, TimestampMixin):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)

    test_case_id: Mapped[str] = mapped_column(String(20), nullable=False)  # TC-001, TC-002
    scenario: Mapped[str] = mapped_column(Text, nullable=False)
    preconditions: Mapped[str] = mapped_column(Text, nullable=False)
    test_steps: Mapped[dict] = mapped_column(JSON, nullable=False)  # Stored as JSON array
    expected_result: Mapped[str] = mapped_column(Text, nullable=False)
    case_type: Mapped[str] = mapped_column(String(20), nullable=False)  # positive, negative, edge
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, approved, rejected

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="test_cases")
    document: Mapped["Document"] = relationship(back_populates="test_cases")
    scripts: Mapped[list["Script"]] = relationship(back_populates="test_case", cascade="all, delete-orphan")
