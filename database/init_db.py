"""
Builds database/hospital.db from schema.sql + seed_data.sql.

Run directly (python3 database/init_db.py) or via scripts/setup.sh.
Safe to re-run: it drops and recreates every table, so it always resets
the demo to a clean state.
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def init_db() -> None:
    os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)

    connection = sqlite3.connect(config.DATABASE_PATH)
    try:
        with open(config.SCHEMA_PATH, "r") as schema_file:
            connection.executescript(schema_file.read())

        with open(config.SEED_PATH, "r") as seed_file:
            connection.executescript(seed_file.read())

        connection.commit()
    finally:
        connection.close()

    print(f"Database initialized at {config.DATABASE_PATH}")


if __name__ == "__main__":
    init_db()
