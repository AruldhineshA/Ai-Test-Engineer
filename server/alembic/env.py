"""
Alembic Environment Configuration
===================================
Configures Alembic to work with our SQLAlchemy models.

KEY CONCEPTS:
- Alembic reads our models and generates migration SQL
- We use SYNC engine for migrations (not async)
- target_metadata tells Alembic about our tables
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import settings
from app.models.base import Base

# Import ALL models so Alembic can detect them
from app.models.project import Project  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.testcase import TestCase  # noqa: F401
from app.models.script import Script  # noqa: F401

# Alembic Config object — access to .ini file values
config = context.config

# Setup Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Our models' metadata — Alembic uses this to detect table changes
target_metadata = Base.metadata

# Override DB URL from our settings (convert async URL to sync for migrations)
sync_url = settings.DATABASE_URL.replace("+asyncpg", "")
config.set_main_option("sqlalchemy.url", sync_url)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Generates SQL script without connecting to the database.
    Useful for: generating SQL to review before running
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    Connects to the database and applies changes directly.
    This is the normal way to run migrations.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
