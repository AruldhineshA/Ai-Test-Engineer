"""
Models Package
==============
Importing all models here ensures SQLAlchemy's registry knows about every
model at startup. Without this, string-based relationships like
`relationship("Script")` will fail because the class hasn't been loaded.
"""

from app.models.base import Base
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.testcase import TestCase
from app.models.script import Script

__all__ = ["Base", "User", "Project", "Document", "TestCase", "Script"]
