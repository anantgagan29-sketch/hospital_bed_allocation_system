"""Data access for allocation_history (append-only audit trail) and system_logs."""
import sqlite3


def record(db: sqlite3.Connection, request_id: str, patient_id: str, bed_id: str,
           action: str, details: str = "") -> None:
    db.execute(
        """INSERT INTO allocation_history (request_id, patient_id, bed_id, action, details)
           VALUES (?, ?, ?, ?, ?)""",
        (request_id, patient_id, bed_id, action, details),
    )


def list_history(db: sqlite3.Connection, limit: int = 200):
    return db.execute(
        "SELECT * FROM allocation_history ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()


def list_logs(db: sqlite3.Connection, limit: int = 100):
    return db.execute(
        "SELECT * FROM system_logs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
