"""Data access for allocation_requests (the "jobs" the scheduler orders)."""
import sqlite3
import uuid

import config


def generate_request_id() -> str:
    return f"REQ-{uuid.uuid4().hex[:6].upper()}"


def next_arrival_time(db: sqlite3.Connection) -> int:
    """Abstract clock: each new request arrives one tick after the last."""
    row = db.execute("SELECT MAX(arrival_time) AS max_t FROM allocation_requests").fetchone()
    return (row["max_t"] or 0) + 1


def create_request(db: sqlite3.Connection, patient_id: str, patient_name: str, age: int,
                    medical_condition: str, urgency: str, required_bed_type: str,
                    burst_time: int) -> str:
    request_id = generate_request_id()
    arrival_time = next_arrival_time(db)
    priority = config.URGENCY_PRIORITY[urgency]

    db.execute(
        """INSERT INTO allocation_requests
           (request_id, patient_id, patient_name, age, medical_condition, urgency,
            required_bed_type, arrival_time, burst_time, priority, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')""",
        (request_id, patient_id, patient_name, age, medical_condition, urgency,
         required_bed_type, arrival_time, burst_time, priority),
    )
    db.commit()
    return request_id


def list_requests(db: sqlite3.Connection):
    return db.execute(
        "SELECT * FROM allocation_requests ORDER BY arrival_time"
    ).fetchall()


def list_pending(db: sqlite3.Connection):
    return db.execute(
        "SELECT * FROM allocation_requests WHERE status IN ('PENDING', 'WAITING') ORDER BY arrival_time"
    ).fetchall()


def get_request(db: sqlite3.Connection, request_id: str):
    return db.execute(
        "SELECT * FROM allocation_requests WHERE request_id = ?", (request_id,)
    ).fetchone()


def update_status(db: sqlite3.Connection, request_id: str, status: str,
                   assigned_bed: str = None, completion_time: int = None) -> None:
    db.execute(
        """UPDATE allocation_requests
           SET status = ?, assigned_bed = COALESCE(?, assigned_bed), completion_time = COALESCE(?, completion_time)
           WHERE request_id = ?""",
        (status, assigned_bed, completion_time, request_id),
    )
