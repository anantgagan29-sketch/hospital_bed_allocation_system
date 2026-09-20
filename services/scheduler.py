"""
Orchestrates CPU-style scheduling over pending allocation requests.

This module only decides ORDER. It has no idea whether a bed actually
exists — that resource check happens next, in allocation_service.py,
following the pipeline in docs/SCHEDULING.md:

    REQUEST QUEUE -> SCHEDULER -> RESOURCE CHECK -> BED ALLOCATION -> COMPLETION
"""
import sqlite3
from typing import List

from models import requests as request_model
from schedulers import fcfs, sjf, srtf, priority, round_robin
from schedulers.base import SchedProcess, ScheduleResult
from services import process_manager

ALGORITHMS = {
    "FCFS": fcfs.schedule,
    "SJF": sjf.schedule,
    "SRTF": srtf.schedule,
    "PRIORITY": priority.schedule,
    "ROUND_ROBIN": round_robin.schedule,
}

ALGORITHM_LABELS = {
    "FCFS": "First-Come, First-Served",
    "SJF": "Shortest Job First",
    "SRTF": "Shortest Remaining Time First",
    "PRIORITY": "Priority Scheduling",
    "ROUND_ROBIN": "Round Robin",
}


def build_sched_processes(db: sqlite3.Connection) -> List[SchedProcess]:
    pending = request_model.list_pending(db)
    sched_processes = []
    for req in pending:
        pid = process_manager.ensure_process(db, req)
        sched_processes.append(SchedProcess(
            pid=pid,
            request_id=req["request_id"],
            patient_name=req["patient_name"],
            arrival_time=req["arrival_time"],
            burst_time=req["burst_time"],
            priority=req["priority"],
        ))
    return sched_processes


def run(db: sqlite3.Connection, algorithm: str, quantum: int = None) -> ScheduleResult:
    algorithm = algorithm.upper()
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unknown scheduling algorithm: {algorithm}")

    sched_processes = build_sched_processes(db)
    if not sched_processes:
        return None

    if algorithm == "ROUND_ROBIN":
        return round_robin.schedule(sched_processes, quantum=quantum)
    return ALGORITHMS[algorithm](sched_processes)


def compare_all(db: sqlite3.Connection, quantum: int = None) -> dict:
    """Runs every algorithm over the SAME pending-request snapshot, purely
    as a scheduling calculation (no bed is actually touched). Used by the
    Scheduling Metrics page to compare algorithms side by side."""
    sched_processes = build_sched_processes(db)
    if not sched_processes:
        return {}

    results = {}
    for name, fn in ALGORITHMS.items():
        if name == "ROUND_ROBIN":
            results[name] = round_robin.schedule(sched_processes, quantum=quantum)
        else:
            results[name] = fn(sched_processes)
    return results
