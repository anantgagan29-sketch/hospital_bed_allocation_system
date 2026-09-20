# OS Concept → Implementation Mapping

| OS Concept | Project Implementation | Evidence (file/page) |
|---|---|---|
| OS Architecture | User → Web UI → Flask → Python runtime → OS interfaces → Linux kernel → hardware | `docs/PROJECT_ARCHITECTURE.md`, `/system` page |
| Kernel & System Calls | `os.getpid()`, `os.listdir()`, `open()`, `subprocess.run()` — Python asking the OS to act on the app's behalf | `services/system_monitor.py::python_os_interface_demo` |
| Linux CLI | Real, read-only commands (`uname`, `ps`, `df`, `free`, `uptime`, `whoami`) run via subprocess | `services/system_monitor.py`, `/linux-monitor` |
| Shell Scripting | 7 Bash scripts: setup, start/stop server, backup, report, cleanup, health check | `scripts/`, `/system` page |
| Process Lifecycle | Allocation request state machine: NEW → READY → RUNNING → WAITING → TERMINATED (+ BLOCKED) | `services/process_manager.py`, `/process-monitor` |
| PCB | `processes` table: pid, state, priority, arrival/burst/waiting/turnaround/response time, assigned bed, program_counter | `models/processes.py`, `/process-monitor` |
| Process vs Threads | Identical workload run via `multiprocessing.Process` vs `threading.Thread`, memory model compared | `services/process_vs_thread.py`, `/process-vs-thread` |
| Multithreading | Real `threading.Thread` workers attempt concurrent bed allocation | `services/concurrency_manager.py`, `/concurrency` |
| Mutual Exclusion / Synchronization | `threading.Lock()` around the check→select→allocate→update critical section | `services/allocation_service.py`, `services/concurrency_manager.py`, `docs/CONCURRENCY.md` |
| CPU Scheduling | Allocation requests ordered as "jobs" before the real resource check | `services/scheduler.py`, `/scheduler` |
| FCFS | Strict arrival-time order | `schedulers/fcfs.py` |
| SJF | Non-preemptive, shortest burst time first among arrived requests | `schedulers/sjf.py` |
| SRTF | Preemptive version of SJF, re-evaluated every time unit | `schedulers/srtf.py` |
| Priority Scheduling | Urgency (CRITICAL/HIGH/MEDIUM/LOW) mapped to priority 1–4; lower number runs first | `schedulers/priority.py`, `config.URGENCY_PRIORITY` |
| Round Robin | Fixed time quantum, requeue if unfinished | `schedulers/round_robin.py` |
| Scheduling Performance Metrics | Waiting/turnaround/response time, throughput, computed and compared across all 5 algorithms | `schedulers/base.py`, `/scheduling-metrics` |
| Resource Management | Beds tracked as AVAILABLE / ALLOCATED / MAINTENANCE per type; release re-triggers waiting requests | `models/beds.py`, `services/allocation_service.py::discharge` |
| Race-Condition Prevention | Deliberately reproducible race (lock OFF) vs safe run (lock ON) | `services/concurrency_manager.py`, `/concurrency` |

## What this project explicitly does NOT claim

Per the assignment brief's restriction on unsupported claims:

- **Not** "Python directly controls the CPU scheduler." → The project
  *simulates* CPU scheduling algorithms at the application level, ordering
  allocation requests. The real Linux kernel scheduler still decides which
  OS thread/process actually executes on a core at any instant.
- **Not** "This is the Linux kernel's real PCB." → `processes` is a
  project-level table *inspired by* PCB theory (the real Linux analog is
  `task_struct`, which this project never touches).
- **Not** "Python makes raw system calls." → `os`/`subprocess`/`open()`
  are standard-library wrappers; the OS performs the actual system call
  underneath them.

## Distinguishing A (simulation) vs B (real OS behaviour)

| | Simulated at application level (A) | Genuinely real OS behaviour (B) |
|---|---|---|
| Scheduling | FCFS/SJF/SRTF/Priority/RR ordering of *requests* | The real Linux CPU scheduler still schedules the OS threads Python creates |
| PCB | `processes` table modeled after PCB theory | The kernel's own `task_struct` for the Flask process itself |
| Processes/Threads | `services/process_vs_thread.py` demo workload | `threading.Thread` / `multiprocessing.Process` are real OS-level constructs — the kernel really does create them |
| Linux commands | N/A | `subprocess.run(["uname","-a"])` genuinely executes on the real kernel |
