"""
Tests for Database connectivity and query execution.
"""

import pandas as pd
from sqlalchemy import text
from src.core.db import get_engine


def test_sqlite_connection_and_table():
    engine = get_engine(use_mysql=False)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) AS total FROM complaints;")).fetchone()
        assert result is not None
        assert result[0] >= 0
