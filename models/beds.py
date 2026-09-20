"""Data access for the beds table (the shared, limited resource)."""
import sqlite3


def list_beds(db: sqlite3.Connection):
    return db.execute("SELECT * FROM beds ORDER BY type, bed_id").fetchall()


def get_bed(db: sqlite3.Connection, bed_id: str):
    return db.execute("SELECT * FROM beds WHERE bed_id = ?", (bed_id,)).fetchone()


def find_available_bed(db: sqlite3.Connection, bed_type: str):
    """Read step of the allocation critical section: find one candidate bed."""
    return db.execute(
        "SELECT * FROM beds WHERE type = ? AND status = 'AVAILABLE' ORDER BY bed_id LIMIT 1",
        (bed_type,),
    ).fetchone()


def allocate_bed(db: sqlite3.Connection, bed_id: str, patient_id: str) -> None:
    """Write step of the allocation critical section. Caller must hold the lock."""
    db.execute(
        """UPDATE beds SET status = 'ALLOCATED', patient_id = ?, allocated_at = datetime('now')
           WHERE bed_id = ?""",
        (patient_id, bed_id),
    )


def release_bed(db: sqlite3.Connection, bed_id: str) -> None:
    db.execute(
        "UPDATE beds SET status = 'AVAILABLE', patient_id = NULL, allocated_at = NULL WHERE bed_id = ?",
        (bed_id,),
    )


def set_maintenance(db: sqlite3.Connection, bed_id: str, in_maintenance: bool) -> None:
    status = "MAINTENANCE" if in_maintenance else "AVAILABLE"
    db.execute("UPDATE beds SET status = ? WHERE bed_id = ?", (status, bed_id))


def counts_by_status(db: sqlite3.Connection) -> dict:
    rows = db.execute("SELECT status, COUNT(*) AS n FROM beds GROUP BY status").fetchall()
    counts = {"AVAILABLE": 0, "ALLOCATED": 0, "MAINTENANCE": 0}
    counts.update({row["status"]: row["n"] for row in rows})
    return counts


def counts_by_type(db: sqlite3.Connection):
    return db.execute(
        "SELECT type, status, COUNT(*) AS n FROM beds GROUP BY type, status"
    ).fetchall()
