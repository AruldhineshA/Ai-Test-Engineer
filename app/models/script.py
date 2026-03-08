"""
Script Database Model (Phase 2)
================================
Stores generated automation scripts linked to test cases.
"""

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Script(Base, TimestampMixin):
    __tablename__ = "scripts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    test_case_id: Mapped[int] = mapped_column(ForeignKey("test_cases.id"), nullable=False)
    script_type: Mapped[str] = mapped_column(String(20), nullable=False)  # playwright, artillery
    language: Mapped[str] = mapped_column(String(20), nullable=False)  # python, javascript
    code_content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="generated")

    # Relationships
    test_case: Mapped["TestCase"] = relationship(back_populates="scripts")
