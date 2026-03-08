"""
Base Database Model
====================
All database models inherit from this base.

LEARN: SQLAlchemy 2.0 uses "Mapped" style
- mapped_column() replaces the old Column()
- Type hints tell SQLAlchemy the column type
- This is the modern way to define models
"""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base class for all database models.
    Every table gets 'id', 'created_at', and 'updated_at' automatically.
    """
    pass


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at to any model.

    LEARN: Mixins let you share columns across models
    without repeating code. DRY principle.
    """
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )
