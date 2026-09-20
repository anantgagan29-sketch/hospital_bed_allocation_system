"""
Turns a scheduling decision into real bed allocations.

The critical section (check availability -> select a bed -> write the
allocation) is wrapped in a module-level threading.Lock. Flask's
development server can handle requests on multiple threads at once, so
without this lock two nearly-simultaneous requests could both read
"bed available" before either had written its allocation back — the
same race condition demonstrated deliberately in
services/concurrency_manager.py. See docs/CONCURRENCY.md.
"""
import sqlite3
import threading

from models import beds as bed_model
from models import requests as request_model
from models import history as history_model
from schedulers.base import ScheduleResult
from services import process_manager

_allocation_lock = threading.Lock()


def _allocate_one(db: sqlite3.Connection, request_row) -> dict:
    """The full critical section for a single request. Caller must already
    hold _allocation_lock."""
    bed = bed_model.find_available_bed(db, request_row["required_bed_type"])
    if bed is None:
        return {"allocated": False, "bed_id": None}

    bed_model.allocate_bed(db, bed["bed_id"], request_row["patient_id"])
    return {"allocated": True, "bed_id": bed["bed_id"]}


def execute_schedule(db: sqlite3.Connection, result: ScheduleResult) -> list:
    """Walk the schedule's finishing order and attempt a real allocation for
    each request, in that order. Returns one outcome dict per request for
    the UI to render alongside the Gantt chart."""
    outcomes = []

    for entry in result.per_process:
        request_row = request_model.get_request(db, entry["request_id"])
        pid = entry["pid"]

        process_manager.mark_running(db, pid)

        with _allocation_lock:
            outcome = _allocate_one(db, request_row)

        if outcome["allocated"]:
            request_model.update_status(
                db, request_row["request_id"], "ALLOCATED",
                assigned_bed=outcome["bed_id"], completion_time=entry["completion_time"],
            )
            process_manager.mark_terminated(
                db, pid, outcome["bed_id"],
                entry["waiting_time"], entry["turnaround_time"], entry["response_time"],
            )
            history_model.record(
                db, request_row["request_id"], request_row["patient_id"], outcome["bed_id"],
                "ALLOCATED",
                f"Scheduled by {result.algorithm}: bed {outcome['bed_id']} assigned.",
            )
        else:
            request_model.update_status(db, request_row["request_id"], "WAITING")
            process_manager.mark_waiting(db, pid)
            history_model.record(
                db, request_row["request_id"], request_row["patient_id"], None,
                "WAITING",
                f"Scheduled by {result.algorithm}: no {request_row['required_bed_type']} bed available.",
            )

        db.commit()
        outcomes.append({**entry, **outcome})

    return outcomes


def discharge(db: sqlite3.Connection, bed_id: str) -> dict:
    """Release a bed, then give the oldest waiting request for that bed type
    a chance at it (resource-release wakes up a waiting request)."""
    bed = bed_model.get_bed(db, bed_id)
    if bed is None or bed["status"] != "ALLOCATED":
        return {"released": False}

    with _allocation_lock:
        bed_model.release_bed(db, bed_id)
        history_model.record(db, None, bed["patient_id"], bed_id, "RELEASED", "Patient discharged.")

        waiting = db.execute(
            """SELECT * FROM allocation_requests
               WHERE status = 'WAITING' AND required_bed_type = ?
               ORDER BY priority, arrival_time LIMIT 1""",
            (bed["type"],),
        ).fetchone()

        reallocated_to = None
        if waiting is not None:
            outcome = _allocate_one(db, waiting)
            if outcome["allocated"]:
                request_model.update_status(db, waiting["request_id"], "ALLOCATED", assigned_bed=outcome["bed_id"])
                process = process_manager.ensure_process(db, waiting)
                process_manager.mark_terminated(db, process, outcome["bed_id"], 0, 0, 0)
                history_model.record(
                    db, waiting["request_id"], waiting["patient_id"], outcome["bed_id"],
                    "ALLOCATED", "Allocated after bed became available from a discharge.",
                )
                reallocated_to = waiting["patient_name"]

        db.commit()

    return {"released": True, "reallocated_to": reallocated_to}
