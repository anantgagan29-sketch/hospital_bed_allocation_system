import os
import sqlite3
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import config


def fresh_db() -> sqlite3.Connection:
    """In-memory database with the schema loaded but no seed data, so each
    test starts from a known, empty state."""
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    with open(config.SCHEMA_PATH) as schema_file:
        connection.executescript(schema_file.read())
    return connection
