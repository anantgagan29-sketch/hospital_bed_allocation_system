"""
Drives the process-lifecycle state machine for allocation requests:

    NEW -> READY -> RUNNING -> (WAITING -> READY)* -> TERMINATED
                                            -> BLOCKED (invalid request)

Every allocation request gets exactly one PCB row (models/processes.py).
This module only changes `state`/`program_counter`; the scheduling
numbers (waiting/turnaround/response time) are filled in once, at
TERMINATED, by services/allocation_service.py using the scheduler's output.
"""
import sqlite3

from models import processes as process_model


def ensure_process(db: sqlite3.Connection, request_row) -> int:
    """Get this request's PCB, creating it (state NEW) if this is its first time
    being seen by the scheduler, then immediately advance it to READY —
    it is now sitting in the request queue waiting for the CPU (the
    allocation engine) to consider it."""
    existing = process_model.get_by_request(db, request_row["request_id"])
    if existing is not None:
        return existing["pid"]

    pid = process_model.create_process(
        db,
        request_id=request_row["request_id"],
        patient_id=request_row["patient_id"],
        priority=request_row["priority"],
        arrival_time=request_row["arrival_time"],
        burst_time=request_row["burst_time"],
    )
    process_model.set_state(db, pid, "READY", "QUEUED_FOR_SCHEDULING")
    db.commit()
    return pid


def mark_running(db: sqlite3.Connection, pid: int) -> None:
    process_model.set_state(db, pid, "RUNNING", "CHECKING_BED_AVAILABILITY")
    db.commit()


def mark_waiting(db: sqlite3.Connection, pid: int) -> None:
    process_model.set_state(db, pid, "WAITING", "NO_BED_AVAILABLE")
    db.commit()


def mark_blocked(db: sqlite3.Connection, pid: int, reason: str) -> None:
    process_model.set_state(db, pid, "BLOCKED", reason)
    db.commit()


def mark_terminated(db: sqlite3.Connection, pid: int, assigned_bed: str,
                     waiting_time: int, turnaround_time: int, response_time: int) -> None:
    process_model.complete_process(db, pid, assigned_bed, waiting_time, turnaround_time, response_time)
    db.commit()
