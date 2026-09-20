# Database Design

SQLite (`database/hospital.db`), built from `database/schema.sql` and
seeded from `database/seed_data.sql` via `database/init_db.py`.

## Tables

### `patients`
| Column | Type | Notes |
|---|---|---|
| patient_id | TEXT PK | `PAT-XXXXXX` |
| name, age, gender, medical_condition, contact | | |
| created_at | TEXT | default `datetime('now')` |

### `beds`
| Column | Type | Notes |
|---|---|---|
| bed_id | TEXT PK | e.g. `ICU-01` |
| ward, type | TEXT | type ∈ ICU/GENERAL/EMERGENCY/PEDIATRIC/ISOLATION |
| status | TEXT | AVAILABLE / ALLOCATED / MAINTENANCE |
| patient_id | TEXT FK → patients | set only while ALLOCATED |
| allocated_at | TEXT | timestamp of the current allocation |

### `allocation_requests`
| Column | Type | Notes |
|---|---|---|
| request_id | TEXT PK | `REQ-XXXXXX` |
| patient_id, patient_name, age, medical_condition | | denormalized for simple, single-query reads |
| urgency | TEXT | CRITICAL/HIGH/MEDIUM/LOW |
| required_bed_type | TEXT | |
| arrival_time, burst_time, priority | INTEGER | scheduling inputs |
| status | TEXT | PENDING / IN_PROGRESS / ALLOCATED / WAITING / REJECTED |
| assigned_bed | TEXT FK → beds | |
| completion_time | INTEGER | scheduler's abstract completion tick |

### `processes` (PCB model)
| Column | Type | Notes |
|---|---|---|
| pid | INTEGER PK AUTOINCREMENT | |
| request_id | TEXT FK → allocation_requests | one PCB per request |
| state | TEXT | NEW/READY/RUNNING/WAITING/BLOCKED/TERMINATED |
| priority, arrival_time, burst_time | INTEGER | copied from the request at creation |
| waiting_time, turnaround_time, response_time | INTEGER | filled in once, at TERMINATED |
| assigned_bed, program_counter | TEXT | |
| creation_time, completion_time | TEXT | |

### `allocation_history`
Append-only audit trail: every ALLOCATED / WAITING / RELEASED event, with
a free-text `details` column. Never updated or deleted, only inserted.

### `system_logs`
General-purpose leveled log table (`level`, `source`, `message`), used
for anything the app wants to record outside the allocation history.

## Relationships

```
patients (1) ----< beds            (a patient occupies at most one bed at a time)
patients (1) ----< allocation_requests
allocation_requests (1) ---- (1) processes   (one PCB per request)
allocation_requests (1) ----< allocation_history
beds (1) ----< allocation_history
```

## Why SQLite and raw SQL, not an ORM

The brief explicitly asks for SQLite and for avoiding unnecessary
complexity. `models/*.py` are thin, single-purpose functions that take an
open `sqlite3.Connection` and run one parameterized query — this keeps
every query visible and auditable, and keeps SQL injection impossible
(every value is passed through `?` placeholders, never string-formatted
into the query).

## Concurrency note

See `docs/CONCURRENCY.md` for why `models/beds.py::find_available_bed()`
and `allocate_bed()` must always be called from inside
`services/allocation_service.py`'s lock, not directly.
