"""
Document Database Model
========================
Stores uploaded documents and their parsed content.
"""

from sqlalchemy import String, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf, docx, md
    parsed_content: Mapped[str | None] = mapped_column(Text, nullable=True)  # Extracted text
    status: Mapped[str] = mapped_column(String(20), default="uploaded")  # uploaded, analyzing, analyzed, failed

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="documents")
    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="document", cascade="all, delete-orphan")
