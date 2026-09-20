# Concurrency, Race Conditions & Synchronization

## The critical section

Every bed allocation, real or demo, follows the same four-step sequence:

```
1. CHECK AVAILABLE BED   (read)
2. SELECT BED            (read)
3. ALLOCATE BED          (write)
4. UPDATE STATE          (write)
```

If two threads execute this sequence at the same time without protection,
both can read "available" before either writes "taken" — both then
allocate the same bed. This is a **race condition**, and the four steps
together are the **critical section**: the region of code that must run
as if only one thread exists at a time (**mutual exclusion**).

## Where this actually happens in the code

- **Real allocation path:** `services/allocation_service.py` wraps
  `_allocate_one()` in a module-level `threading.Lock()`
  (`_allocation_lock`). Flask's development server can run multiple
  requests concurrently on different threads, so two nearly-simultaneous
  "Run & Allocate" or discharge requests really could race without it.
- **Deliberate demo:** `services/concurrency_manager.py::RaceConditionDemo`
  runs the identical critical section against an **isolated, in-memory**
  pool of demo beds (never real hospital data), so it can be re-run safely
  and repeatedly. A short `time.sleep()` between the check and the write
  widens the race window so the bug shows up reliably instead of only
  occasionally.

## Without the lock

```
Thread A checks bed-101 -> available
Thread B checks bed-101 -> available   (A hasn't written yet)
Thread A allocates bed-101
Thread B allocates bed-101             <- CONFLICT: two patients, one bed
```

`tests/test_concurrency.py::test_tc02_without_lock_two_threads_same_bed_can_conflict`
proves this happens by asserting `conflicting_allocations > 0`.

## With the lock

```
Thread A: waits for lock -> acquires -> checks (available) -> allocates -> releases
Thread B: waits for lock (blocked until A releases) -> acquires -> checks (NOW unavailable) -> waits
```

`tests/test_concurrency.py::test_tc08_lock_prevents_conflicting_allocations`
proves `conflicting_allocations == 0` with the lock enabled, no matter how
many threads compete for the single bed.

## Why SQLite alone isn't enough

SQLite guarantees a single SQL statement is atomic, but the allocation
critical section is **multiple statements**: a `SELECT` to find an
available bed, followed by an `UPDATE` to claim it. Two threads can both
finish their `SELECT` before either runs its `UPDATE` — SQLite's own
locking does not protect a sequence of statements, only each one
individually. That's exactly why an explicit `threading.Lock()` is still
required even though the database itself has internal locking.

## Deadlock (why it isn't a risk here)

Deadlock requires (at minimum) two or more locks acquired in inconsistent
orders by different threads (circular wait). This project uses exactly
one lock per manager (`_allocation_lock` for real allocation, one
`RaceConditionDemo.lock` per demo run), and no code path ever tries to
acquire a second lock while already holding one — so circular wait cannot
occur. This is discussed for completeness since deadlock is part of the
Unit syllabus, not because the project needed to solve it.

## Process vs Thread (docs/OS_CONCEPT_MAPPING.md has the full table)

`services/process_vs_thread.py` runs the same workload with
`threading.Thread` and with `multiprocessing.Process`:

- **Threads** share the enclosing process's memory directly — which is
  exactly why they need a lock to touch shared state safely.
- **Processes** have separate memory spaces; sharing a result back
  requires explicit IPC (here, a `multiprocessing.Queue`).
