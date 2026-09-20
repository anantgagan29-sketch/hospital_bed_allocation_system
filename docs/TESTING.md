# Testing

Automated tests live in `tests/` (unittest, pytest-compatible):

```bash
pip install pytest
python3 -m pytest tests/ -v
```

## Test case matrix

| ID | Scenario | Automated test |
|---|---|---|
| TC01 | Two requests, one available bed | `test_allocation_service.py::test_tc01_two_requests_one_bed` |
| TC02 | Two threads race for the same bed (no lock) | `test_concurrency.py::test_tc02_without_lock_two_threads_same_bed_can_conflict` |
| TC03 | Critical patient vs low-priority patient | `test_allocation_service.py::test_tc03_critical_beats_low_priority` |
| TC04 | No beds available | `test_allocation_service.py::test_tc04_no_beds_available` |
| TC05 | Bed becomes available after discharge | `test_allocation_service.py::test_tc05_discharge_frees_bed_for_waiting_request` |
| TC06 | SRTF scheduling (preemption) | `test_schedulers.py::TestSRTF::test_shorter_job_preempts_running_one` |
| TC07 | Round Robin scheduling (fair turns) | `test_schedulers.py::TestRoundRobin` (2 tests) |
| TC08 | Race condition prevented by lock | `test_concurrency.py::test_tc08_lock_prevents_conflicting_allocations` |
| TC09 | Linux command execution (whitelist) | `test_system_monitor.py::test_tc09_*` |
| TC10 | Shell script execution (whitelist) | `test_system_monitor.py::test_tc10_*` |
| TC11 | Invalid request (missing/bad form fields) | Manual — see "Manual checks" below |
| TC12 | Database failure (missing table / bad path) | Manual — see "Manual checks" below |

Plus `test_schedulers.py::TestFCFS::test_known_example`, which checks FCFS
against a hand-computed textbook example (average waiting time = 5.75).

## Manual checks (TC11, TC12 and general UI smoke test)

**TC11 — invalid request:**
1. Go to `/requests` and submit the form with `burst_time` left blank or
   set to `0`.
2. Expected: a red flash message ("Burst time must be a positive whole
   number.") and no row inserted — verified by `routes/request_routes.py`'s
   validation before calling `create_request`.

**TC12 — database failure:**
1. Temporarily rename `database/hospital.db` while the server is stopped.
2. Start the server and open any page that queries the DB.
3. Expected: Flask raises `sqlite3.OperationalError: no such table`,
   visible as a 500 error in debug mode — this confirms the app does not
   silently swallow database errors. Restore the file (or re-run
   `python3 database/init_db.py`) afterwards.

## Full manual demo checklist

Walk through `README.md`'s "Demo scenario" section end-to-end once before
the viva: register patients, create 5 requests with mixed urgency, run
FCFS then Priority, compare on Scheduling Metrics, check Process Monitor
states, run the Concurrency Demo with the lock off then on, check the
Linux Monitor, run `system_report.sh` from the OS Lab page, and discharge
a patient to confirm a waiting request gets reallocated.
