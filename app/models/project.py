"""
Project Database Model
=======================
Represents a testing project that groups documents and test cases.

LEARN: SQLAlchemy Relationships
- relationship() creates a link between tables
- "back_populates" sets up bidirectional access:
  project.documents → list of documents
  document.project → the parent project
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships — access related data easily
    documents: Mapped[list["Document"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="project", cascade="all, delete-orphan")
