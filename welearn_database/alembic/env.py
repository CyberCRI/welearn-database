import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import URL

from welearn_database.database_utils import create_sqlalchemy_engine

EXCLUDE_SCHEMAS_NAMES = ["public"]

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# here we allow ourselves to pass interpolation vars to alembic.ini
# fron the host env
section = config.config_ini_section

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from welearn_database.data.models import Base

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Targets that ask the user to type their name before an online run.
PROTECTED_TARGETS = {"prod"}


def load_target_env() -> str | None:
    """Load the database settings for the target given with `-x env=<name>`.

    With the flag, `.env.<name>` at the repository root is loaded and its values
    override variables already exported in the shell. Without it, `.env` is
    loaded as before and exported variables win.
    """
    target = context.get_x_argument(as_dictionary=True).get("env")
    root = Path(config.config_file_name or "alembic.ini").resolve().parent

    if not target:
        load_dotenv(root / ".env")
        return None

    env_file = root / f".env.{target}"
    if not env_file.is_file():
        available = sorted(
            p.name for p in root.glob(".env.*") if p.name != ".env.example"
        )
        raise SystemExit(
            f"No {env_file.name} found in {root}. "
            f"Available: {', '.join(available) or 'none'}"
        )
    load_dotenv(env_file, override=True)
    return target


def confirm_target(target: str | None) -> None:
    """Print where the migration goes, and ask before touching a protected database."""
    host = os.getenv("PG_HOST", "")
    db = os.getenv("PG_DB", "")
    label = target or ".env"
    print(f"Target: {label} -> {host}/{db}", file=sys.stderr)

    if context.is_offline_mode():
        return

    if target in PROTECTED_TARGETS or "prod" in host.lower():
        expected = target or "prod"
        answer = input(f"Type '{expected}' to run against this database: ")
        if answer.strip() != expected:
            raise SystemExit("Aborted.")


TARGET = load_target_env()
confirm_target(TARGET)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    db_url = URL.create(
        drivername=os.getenv("PG_DRIVER", "postgresql+psycopg"),
        username=os.environ["PG_USER"],
        password=os.environ["PG_PASSWORD"],
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", "5432")),
        database=os.environ["PG_DB"],
    )
    context.configure(
        url=db_url.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema="public",
    )

    with context.begin_transaction():
        context.run_migrations()


def include_name(name, type_, parent_names):
    if type_ == "schema" and name in EXCLUDE_SCHEMAS_NAMES:
        return False
    elif type_ == "index":
        return False

    return True


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_sqlalchemy_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema="public",
            include_schemas=True,
            include_name=include_name,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
