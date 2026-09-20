-- Hospital Bed Allocation Platform — database schema
-- SQLite. Run via database/init_db.py (also called by scripts/setup.sh).

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS system_logs;
DROP TABLE IF EXISTS allocation_history;
DROP TABLE IF EXISTS processes;
DROP TABLE IF EXISTS allocation_requests;
DROP TABLE IF EXISTS beds;
DROP TABLE IF EXISTS patients;

-- Patients ------------------------------------------------------------
CREATE TABLE patients (
    patient_id        TEXT PRIMARY KEY,
    name              TEXT NOT NULL,
    age               INTEGER NOT NULL,
    gender            TEXT,
    medical_condition TEXT,
    contact           TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Beds ------------------------------------------------------------------
-- status: AVAILABLE | ALLOCATED | MAINTENANCE
CREATE TABLE beds (
    bed_id       TEXT PRIMARY KEY,
    ward         TEXT NOT NULL,
    type         TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'AVAILABLE',
    patient_id   TEXT,
    allocated_at TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- Allocation requests -----------------------------------------------------
-- One row per bed request a patient makes. This is the "job" that the
-- scheduler orders and the process model tracks the lifecycle of.
-- status: PENDING | IN_PROGRESS | ALLOCATED | WAITING | REJECTED
CREATE TABLE allocation_requests (
    request_id        TEXT PRIMARY KEY,
    patient_id        TEXT NOT NULL,
    patient_name      TEXT NOT NULL,
    age               INTEGER NOT NULL,
    medical_condition TEXT,
    urgency           TEXT NOT NULL,
    required_bed_type TEXT NOT NULL,
    arrival_time      INTEGER NOT NULL,
    burst_time        INTEGER NOT NULL,
    priority          INTEGER NOT NULL,
    status            TEXT NOT NULL DEFAULT 'PENDING',
    assigned_bed      TEXT,
    completion_time   INTEGER,
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (assigned_bed) REFERENCES beds(bed_id)
);

-- Processes (PCB model) ---------------------------------------------------
-- One PCB per allocation request. state follows NEW -> READY -> RUNNING ->
-- (WAITING <-> READY)* -> TERMINATED, with BLOCKED for invalid/error requests.
CREATE TABLE processes (
    pid              INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id       TEXT NOT NULL,
    patient_id       TEXT NOT NULL,
    state            TEXT NOT NULL DEFAULT 'NEW',
    priority         INTEGER NOT NULL,
    arrival_time     INTEGER NOT NULL,
    burst_time       INTEGER NOT NULL,
    waiting_time     INTEGER,
    turnaround_time  INTEGER,
    response_time    INTEGER,
    assigned_bed     TEXT,
    program_counter  TEXT NOT NULL DEFAULT 'REQUEST_RECEIVED',
    creation_time    TEXT NOT NULL DEFAULT (datetime('now')),
    completion_time  TEXT,
    FOREIGN KEY (request_id) REFERENCES allocation_requests(request_id)
);

-- Allocation history -------------------------------------------------------
-- Append-only audit trail: every state change / allocation / release.
CREATE TABLE allocation_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id  TEXT,
    patient_id  TEXT,
    bed_id      TEXT,
    action      TEXT NOT NULL,
    timestamp   TEXT NOT NULL DEFAULT (datetime('now')),
    details     TEXT
);

-- System logs ---------------------------------------------------------------
CREATE TABLE system_logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp  TEXT NOT NULL DEFAULT (datetime('now')),
    level      TEXT NOT NULL DEFAULT 'INFO',
    source     TEXT NOT NULL,
    message    TEXT NOT NULL
);

CREATE INDEX idx_beds_status ON beds(status);
CREATE INDEX idx_requests_status ON allocation_requests(status);
CREATE INDEX idx_processes_state ON processes(state);
