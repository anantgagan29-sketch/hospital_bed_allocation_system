"""
Data access for the processes table: the PCB (Process Control Block) model.

This is a project-level PCB inspired by OS theory, not the Linux kernel's
real PCB (task_struct). See docs/OS_CONCEPT_MAPPING.md.
"""
import sqlite3


def create_process(db: sqlite3.Connection, request_id: str, patient_id: str,
                    priority: int, arrival_time: int, burst_time: int) -> int:
    cursor = db.execute(
        """INSERT INTO processes (request_id, patient_id, state, priority, arrival_time, burst_time,
                                   program_counter)
           VALUES (?, ?, 'NEW', ?, ?, ?, 'REQUEST_RECEIVED')""",
        (request_id, patient_id, priority, arrival_time, burst_time),
    )
    db.commit()
    return cursor.lastrowid


def set_state(db: sqlite3.Connection, pid: int, state: str, program_counter: str = None) -> None:
    if program_counter is not None:
        db.execute("UPDATE processes SET state = ?, program_counter = ? WHERE pid = ?",
                   (state, program_counter, pid))
    else:
        db.execute("UPDATE processes SET state = ? WHERE pid = ?", (state, pid))


def complete_process(db: sqlite3.Connection, pid: int, assigned_bed: str, waiting_time: int,
                      turnaround_time: int, response_time: int) -> None:
    db.execute(
        """UPDATE processes
           SET state = 'TERMINATED', program_counter = 'ALLOCATION_COMPLETE',
               assigned_bed = ?, waiting_time = ?, turnaround_time = ?, response_time = ?,
               completion_time = datetime('now')
           WHERE pid = ?""",
        (assigned_bed, waiting_time, turnaround_time, response_time, pid),
    )


def get_by_request(db: sqlite3.Connection, request_id: str):
    return db.execute("SELECT * FROM processes WHERE request_id = ?", (request_id,)).fetchone()


def list_processes(db: sqlite3.Connection):
    return db.execute("SELECT * FROM processes ORDER BY pid DESC").fetchall()


def list_active(db: sqlite3.Connection):
    return db.execute(
        "SELECT * FROM processes WHERE state != 'TERMINATED' ORDER BY pid"
    ).fetchall()
