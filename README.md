# Hospital Bed Allocation Platform

**Course:** Operating Systems (CCSE0303A) — B.Tech CSE-AI, Group 1
**Team:** Anant Pratap Singh, Aman Maurya, Akash Yadav, Abhijeet Chaudhary, Alok

A working Flask + SQLite web application that allocates hospital beds to
patients — and, more importantly for this course, genuinely *implements*
Operating Systems concepts rather than just mentioning them in a report:

- Every allocation request is modeled as a **process** with a **PCB**
  (Process Control Block) and a real lifecycle (NEW → READY → RUNNING →
  WAITING → TERMINATED).
- A shared, limited resource (beds) is allocated through **five real CPU
  scheduling algorithms** (FCFS, SJF, SRTF, Priority, Round Robin) with the
  standard metrics (waiting/turnaround/response time, throughput).
- Concurrent requests are handled with real **Python threads**, and a
  dedicated demo proves — by actually triggering it — why the allocation
  critical section needs a `threading.Lock()`.
- A **Linux System Monitor** runs real, whitelisted Linux commands via
  `subprocess`, and seven **Bash scripts** in `scripts/` automate setup,
  running, backup, reporting and cleanup.

See `docs/` for the full write-up: architecture, the OS-concept mapping
table, scheduling formulas, concurrency/synchronization details, database
design, the test plan, and a 35-question Viva Mode study sheet (also
live in the app at `/viva`).

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 database/init_db.py
python3 app.py
```

Open http://localhost:5000 (if that port is taken — e.g. by AirPlay
Receiver on macOS — run `PORT=5001 python3 app.py` instead).

Or, once you're on Linux, use the provided scripts:

```bash
chmod +x scripts/*.sh
./scripts/setup.sh
./scripts/start_server.sh
```

## Project layout

```
hospital-bed-allocation/
├── app.py                  Flask entry point (registers all blueprints)
├── config.py                Constants: DB paths, urgency->priority map, command whitelist
├── database/                 schema.sql, seed_data.sql, init_db.py
├── models/                    Thin data-access functions per table
├── schedulers/                 One file per algorithm: fcfs, sjf, srtf, priority, round_robin
├── services/                    allocation_service, scheduler, process_manager,
│                                concurrency_manager, process_vs_thread, system_monitor
├── routes/                       One Flask blueprint per page
├── data/viva_questions.py         Viva Mode question bank
├── templates/, static/             Bootstrap 5 + Chart.js UI
├── scripts/                        7 Bash scripts (setup/start/stop/backup/report/cleanup/health)
├── tests/                           unittest test suite (pytest-compatible)
└── docs/                            Architecture, OS mapping, scheduling, concurrency, etc.
```

## Running the tests

```bash
pip install pytest
python3 -m pytest tests/ -v
```

## Demo scenario (also see docs/TESTING.md)

1. Register a few patients, then create 5 allocation requests with mixed
   urgency levels and bed types.
2. Open **Scheduler**, run **FCFS**, note the Gantt chart and metrics.
3. Run **Priority Scheduling** on the same queue and compare — see
   **Scheduling Metrics** for a side-by-side of all five algorithms.
4. Open **Process Monitor** to see each request's PCB and lifecycle state.
5. Open **Concurrency Demo**, run it with the lock OFF (watch conflicting
   allocations appear), then ON (conflicts drop to zero).
6. Open **Linux Monitor** to see `uname`, `ps`, `df`, `uptime` running for
   real, then go to **OS Lab / System** and run `system_report.sh`.
7. Discharge a patient from **Beds** and watch a waiting request get
   allocated automatically.
8. Open **Viva Mode** for the full Q&A study sheet.

## Important academic note

This project **simulates** CPU scheduling and the PCB at the application
level. It does not modify the Linux kernel's real scheduler or its real
`task_struct`. Every place this distinction matters is called out in the
code comments and in `docs/OS_CONCEPT_MAPPING.md`.
