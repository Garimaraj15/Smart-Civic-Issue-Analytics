"""
Database connection and management module.
Supports embedded SQLite (zero-config, portable) and MySQL (production/enterprise).
"""

from urllib.parse import quote_plus
from sqlalchemy import create_engine, Engine
from src.core.config import (
    DB_TYPE,
    SQLITE_DB_PATH,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_DATABASE,
)
from src.core.logger import get_logger

logger = get_logger("DatabaseManager")


def get_engine(use_mysql: bool = False) -> Engine:
    """
    Returns an active SQLAlchemy database engine.
    Defaults to SQLite for seamless portability unless use_mysql=True or DB_TYPE='mysql'.
    """
    if use_mysql or DB_TYPE == "mysql":
        try:
            password_encoded = quote_plus(MYSQL_PASSWORD) if MYSQL_PASSWORD else ""
            mysql_url = f"mysql+mysqlconnector://{MYSQL_USER}:{password_encoded}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
            engine = create_engine(mysql_url, echo=False)
            with engine.connect() as conn:
                pass
            logger.info(f"Connected to MySQL Database: {MYSQL_DATABASE}@{MYSQL_HOST}")
            return engine
        except Exception as e:
            logger.warning(
                f"MySQL connection failed: {e}. Falling back to SQLite database."
            )

    # SQLite fallback / default
    sqlite_url = f"sqlite:///{SQLITE_DB_PATH}"
    engine = create_engine(sqlite_url, echo=False)
    logger.info(f"Connected to SQLite Database: {SQLITE_DB_PATH}")
    return engine
