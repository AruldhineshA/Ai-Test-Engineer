"""
File Handler Utilities
=======================
Common file operations used across the application.
"""

from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}


def validate_file_extension(filename: str) -> bool:
    """Check if the file extension is allowed."""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def get_file_extension(filename: str) -> str:
    """Get the file extension without the dot."""
    return Path(filename).suffix.lower().lstrip(".")
