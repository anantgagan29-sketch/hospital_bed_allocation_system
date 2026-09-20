"""
SQLite connection helpers.

Design note (relevant to the Synchronization module): SQLite connections are
not safe to share across threads. Rather than hand one connection to every
thread, get_connection() opens a short-lived connection per caller. Combined
with SQLite's own file-level locking, this is what lets services/concurrency_manager.py
run multiple threads safely while still needing an explicit threading.Lock
around the check-then-allocate critical section (SQLite alone only protects
a single statement, not the multi-step "check availability, then write"
sequence — see docs/CONCURRENCY.md).
"""
import sqlite3

from flask import g

import config


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(config.DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_db() -> sqlite3.Connection:
    """Per-Flask-request connection, reused across the request via flask.g."""
    if "db" not in g:
        g.db = get_connection()
    return g.db


def close_db(_exception=None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def log_event(source: str, message: str, level: str = "INFO", connection: sqlite3.Connection = None) -> None:
    owns_connection = connection is None
    connection = connection or get_connection()
    connection.execute(
        "INSERT INTO system_logs (level, source, message) VALUES (?, ?, ?)",
        (level, source, message),
    )
    if owns_connection:
        connection.commit()
        connection.close()
