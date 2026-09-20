# Project Architecture

## Layered view

```mermaid
flowchart TD
    U[User] --> W[Web UI - Bootstrap + Chart.js]
    W --> F[Flask Application - app.py + routes/]
    F --> E[Hospital Allocation Engine]
    subgraph E[Hospital Allocation Engine]
        PM[Process Manager<br/>PCB / lifecycle]
        SCH[Scheduler<br/>FCFS · SJF · SRTF · Priority · RR]
        CM[Concurrency Manager<br/>threading.Lock]
        RM[Resource Manager<br/>beds]
        LM[Linux Monitor<br/>whitelisted subprocess]
    end
    E --> DB[(SQLite)]
    E --> OS[Linux OS]
    DB --> OS
    OS --> K[Kernel]
    K --> HW[CPU / Memory / Disk / Network]
```

This is the picture referenced throughout the code comments. Two things
are true at once, and the project is careful never to blur them:

- **A (application-level simulation):** the scheduler, PCB and process
  lifecycle are built entirely in Python/Flask, to *teach and demonstrate*
  OS concepts.
- **B (real OS behaviour):** the Linux Monitor, the shell scripts, and the
  actual thread/process creation via Python's `threading`/`multiprocessing`
  modules genuinely execute on top of the real Linux kernel — nothing
  there is mocked.

## Request lifecycle through the layers

1. A patient's allocation request is submitted through the Web UI
   (`templates/requests.html` → `routes/request_routes.py`).
2. It is stored as a row in `allocation_requests` (a "job") via
   `models/requests.py`.
3. When an admin runs the Scheduler, `services/scheduler.py` builds one
   PCB per request (`services/process_manager.py` + `models/processes.py`)
   and calls the chosen algorithm in `schedulers/`.
4. `services/allocation_service.py` walks the algorithm's finishing order
   and, for each request, performs the real resource check — this is the
   guarded critical section (see `docs/CONCURRENCY.md`).
5. Every allocation or wait is written to `allocation_history` for audit
   (`models/history.py`), and the PCB is advanced to `TERMINATED` or
   `WAITING`.
6. Flask, in turn, only reaches SQLite and the filesystem through Python's
   standard library, which itself asks the OS to do the work — see
   `docs/OS_CONCEPT_MAPPING.md` for the exact system-call-level examples.

## Process lifecycle diagram

```mermaid
stateDiagram-v2
    [*] --> NEW: Request created
    NEW --> READY: Queued for scheduling
    READY --> RUNNING: Scheduler selects this request
    RUNNING --> WAITING: No matching bed available
    WAITING --> READY: Bed freed by a discharge, re-queued
    RUNNING --> TERMINATED: Bed successfully allocated
    NEW --> BLOCKED: Invalid request
    [*] --> BLOCKED
    TERMINATED --> [*]
```

## Bed allocation workflow

```mermaid
flowchart LR
    A[Request Queue] --> B[Scheduler]
    B --> C[Resource Check]
    C -->|Bed available| D[Bed Allocation]
    C -->|No bed available| E[WAITING]
    D --> F[Process Completion]
    E -.->|Discharge frees a bed| C
```

## Thread synchronization

```mermaid
sequenceDiagram
    participant T1 as Thread A
    participant T2 as Thread B
    participant L as Lock
    participant Bed as Shared Bed

    T1->>L: acquire()
    activate L
    T1->>Bed: check available? yes
    T1->>Bed: allocate
    T1->>L: release()
    deactivate L
    T2->>L: acquire() (was blocked until now)
    activate L
    T2->>Bed: check available? no
    T2->>T2: mark WAITING
    T2->>L: release()
    deactivate L
```

## CPU scheduling (example: Priority)

```mermaid
gantt
    dateFormat X
    axisFormat %s
    section Requests
    P1 (Critical) :done, p1, 0, 5
    P5 (Critical) :done, p5, 5, 10
    P3 (High)     :done, p3, 10, 16
    P4 (Medium)   :done, p4, 16, 22
    P2 (Low)      :done, p2, 22, 28
```

## Why Flask + SQLite + vanilla JS

The brief explicitly asks for a stack that demonstrates OS concepts
clearly, not one that demonstrates enterprise architecture skills. React,
Docker, Kubernetes, Redis and microservices would add real infrastructure
concepts to learn (containers, orchestration, caching) that are outside
this course's syllabus and would dilute the OS focus. Flask + SQLite +
Bootstrap/Chart.js keeps every extra concept in the room related to
Operating Systems.
