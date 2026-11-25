import logging
import os

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


def create_db_session():
    engine = create_sqlalchemy_engine()
    session_made = sessionmaker(engine)
    return session_made()


def create_sqlalchemy_engine(connect_timeout: int | None = None):
    """Engine for the database in the PG_* variables.

    `connect_timeout` (seconds) makes a connection to an unreachable host fail
    instead of waiting for the TCP timeout of the system.
    """
    pg_driver = os.getenv("PG_DRIVER", "postgresql+psycopg2")
    pg_user = os.getenv("PG_USER")
    pg_password = os.getenv("PG_PASSWORD")
    pg_host = os.getenv("PG_HOST")
    pg_port = os.getenv("PG_PORT")
    pg_db = os.getenv("PG_DB")
    url_object = URL.create(
        drivername=pg_driver,
        username=pg_user,
        password=pg_password,
        host=pg_host,
        port=pg_port,
        database=pg_db,
    )
    connect_args = (
        {} if connect_timeout is None else {"connect_timeout": connect_timeout}
    )
    engine = create_engine(url_object, connect_args=connect_args)
    return engine
