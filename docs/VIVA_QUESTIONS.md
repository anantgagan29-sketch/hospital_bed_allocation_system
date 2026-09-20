# Viva Questions & Answers

36 questions covering every OS topic in the assignment brief. Also available live, with a search-friendly accordion UI, at `/viva`.

## OS Architecture

**Q: What layers sit between this web app and the hardware?**

A: User -> Flask app -> Python runtime -> OS system calls/interfaces -> Linux kernel -> CPU/Memory/Disk. Every allocation request eventually becomes kernel-managed work: process/thread creation, file I/O for SQLite, and CPU scheduling.

**Q: Where does the kernel actually appear in this project?**

A: We never touch the kernel directly. Instead, Python's os/subprocess/threading modules ask the kernel to do things for us — the Linux Monitor page shows this by running real commands like uname and ps through subprocess.run().

## Kernel & System Calls

**Q: Does this project make raw system calls?**

A: No — it makes system calls indirectly, through Python's standard library, which itself calls the OS. os.getpid(), os.listdir(), open(), and subprocess.run() are all examples used here.

**Q: What does subprocess.run() actually do at the OS level?**

A: It asks the OS to create a new child process (fork/exec on Linux) to run the given program, then lets the parent (Flask) read its stdout/stderr once it finishes.

## Linux CLI

**Q: Which Linux commands does the Linux System Monitor page run?**

A: uname -a, whoami, pwd, ls, df -h, free -h, uptime, ps -e, and ps aux — all read-only, and all from a fixed whitelist in config.ALLOWED_LINUX_COMMANDS.

**Q: Why is a whitelist used instead of accepting a command from the user?**

A: Running an arbitrary string from user input through a shell is a command-injection vulnerability. The whitelist means only pre-approved, fixed argument lists can ever run.

**Q: What does `ps aux | wc -l` tell you, and how is it built safely here?**

A: It counts running processes. We never construct a shell pipe string; we run `ps aux` via subprocess, then count the lines in Python — the same result without shell-string concatenation.

## Shell Scripting

**Q: What do the shell scripts in scripts/ do?**

A: setup.sh prepares the environment and DB; start_server.sh/stop_server.sh manage the Flask process; backup_database.sh snapshots the SQLite file; system_report.sh gathers OS/CPU/memory/disk stats into reports/; cleanup.sh removes caches/old reports; health_check.sh pings the running server.

**Q: Why chmod +x scripts/*.sh?**

A: A shell script needs the execute permission bit set before it can be run directly (./script.sh) instead of only being read by `bash script.sh`.

**Q: What OS concepts do the scripts demonstrate?**

A: Shell variables, redirection (> to write reports/system_report.txt), pipes, exit codes checked with $?, and conditional statements to fail fast if a step doesn't succeed.

## Process Lifecycle

**Q: What are the states an allocation request moves through?**

A: NEW -> READY -> RUNNING -> (WAITING -> READY again once a bed frees up) -> TERMINATED, with BLOCKED reserved for invalid requests. This mirrors the OS process lifecycle model.

**Q: What triggers the WAITING state?**

A: When the scheduler picks a request (RUNNING) but the resource check finds no bed of the required type available — the request can't proceed, so it moves to WAITING, just like a process blocked on an unavailable resource.

## PCB

**Q: What is a PCB and where is it in this project?**

A: A Process Control Block is the OS's per-process bookkeeping record. Our `processes` table mirrors that idea for allocation requests: pid, state, priority, arrival/burst time, waiting/turnaround/response time, assigned bed, and a program_counter field.

**Q: Is this the real Linux kernel PCB?**

A: No. It's a project-level model inspired by PCB theory (task_struct is the real Linux equivalent), built to make the request lifecycle visible and measurable, not to modify the kernel.

**Q: What does program_counter mean in our PCB, given there's no real CPU instruction pointer?**

A: We reuse the field name from PCB theory to record which STEP of the allocation pipeline the request is at (e.g. QUEUED_FOR_SCHEDULING, CHECKING_BED_AVAILABILITY), which plays the same conceptual role as "where execution currently is".

## Process vs Thread

**Q: How does this project demonstrate the difference between processes and threads?**

A: The /process-vs-thread page runs the identical workload once with threading.Thread workers and once with multiprocessing.Process workers, and reports each one's measured time and memory model.

**Q: What's the key difference in memory sharing?**

A: Threads share the same process memory, so they can read/write the same Python objects directly (which is exactly why locks are needed). Processes have separate memory spaces and must explicitly pass data back, e.g. via a multiprocessing.Queue.

## Multithreading

**Q: Where is real Python threading used in this project?**

A: In services/concurrency_manager.py's race-condition demo, and inside allocation_service.py's real allocation path, both of which can run on multiple Flask worker threads at once.

**Q: Why can Flask handle multiple requests with threads at all?**

A: Flask's development server runs with threading enabled by default, so two nearly-simultaneous HTTP requests can be executing Python code concurrently — which is exactly the scenario that makes bed allocation a shared-resource problem.

## Synchronization

**Q: What is the critical section in this project?**

A: Check available bed -> select a bed -> allocate it -> update the database. If two threads run this sequence at the same time without protection, both can select the same bed.

**Q: How is mutual exclusion enforced?**

A: A threading.Lock() (in both allocation_service.py and concurrency_manager.py) wraps the critical section so only one thread executes it at a time; every other thread blocks until the lock is released.

**Q: Doesn't SQLite already prevent this by itself?**

A: SQLite guarantees a single statement is atomic, but our critical section is multiple statements (a SELECT followed by an UPDATE). Without an explicit lock, two threads could both complete their SELECT before either runs its UPDATE — the classic check-then-act race.

## Race Condition

**Q: Walk through the race condition without a lock.**

A: Thread A checks bed-101 -> available. Thread B checks bed-101 -> also available (A hasn't written yet). Thread A allocates bed-101. Thread B also allocates bed-101. Now one bed has two patients.

**Q: How does the demo page prove this happens?**

A: The Concurrency & Race Condition Demo runs N threads against a small in-memory bed pool. Without the lock, running it several times will show "conflicting allocations" > 0 — the same bed_id handed to more than one thread. With the lock enabled, conflicts are always 0.

## CPU Scheduling

**Q: What does the scheduler actually schedule here?**

A: Not the real CPU — it orders allocation REQUESTS (modeled as processes with arrival_time, burst_time, priority) to decide which one the allocation engine should try to satisfy next.

## FCFS

**Q: How does FCFS decide the order?**

A: Strictly by arrival_time — whichever request arrived first is processed first, regardless of urgency or estimated processing time.

## SJF

**Q: How does SJF differ from FCFS?**

A: SJF (non-preemptive) picks, among requests that have already arrived, the one with the smallest burst_time next — it can reduce average waiting time but can starve long requests.

## SRTF

**Q: What makes SRTF preemptive?**

A: SRTF re-evaluates every time unit: if a newly arrived request has a smaller REMAINING burst time than the one currently running, it takes over immediately, unlike SJF which commits once a request starts.

## Priority Scheduling

**Q: How does priority scheduling map to hospital urgency?**

A: config.URGENCY_PRIORITY converts CRITICAL/HIGH/MEDIUM/LOW into priority numbers 1-4 (lower = more urgent). The scheduler always picks the lowest available priority number next, so a CRITICAL request jumps ahead of a LOW one that arrived earlier.

## Round Robin

**Q: What is the time quantum and what happens when it expires?**

A: Each request gets at most `quantum` time units per turn. If it isn't finished, it goes to the back of the ready queue and waits its turn again — this bounds how long any one request can occupy the allocation engine before others get a chance.

## Scheduling Metrics

**Q: Define waiting time, turnaround time, response time, and throughput.**

A: Waiting Time = Turnaround Time - Burst Time. Turnaround Time = Completion Time - Arrival Time. Response Time = First Start Time - Arrival Time. Throughput = Completed Processes / Total Execution Time.

**Q: Why compare multiple algorithms on the same request set?**

A: The Scheduling Metrics page runs all five algorithms against the identical pending-request snapshot so the average waiting/turnaround/response times and throughput are a fair, apples-to-apples comparison.

## Resource Management

**Q: What is the limited resource in this system?**

A: Hospital beds, tracked per type (ICU/General/Emergency/Pediatric/Isolation). Each bed can be AVAILABLE, ALLOCATED, or MAINTENANCE, and allocation can only succeed if a matching-type bed is AVAILABLE.

**Q: What happens on discharge?**

A: The bed is released back to AVAILABLE, and the system immediately checks whether any WAITING request of that bed type can now be satisfied — resource release re-triggers scheduling for the waiting queue.

## Deadlock

**Q: Can this system deadlock?**

A: Not in the classic sense — there's only one shared resource type per bed category and a single lock guarding allocation, so there's no circular-wait between multiple locks. It's included conceptually in docs/CONCURRENCY.md for completeness.

## Security

**Q: How does the project avoid SQL injection?**

A: Every database query uses parameterized placeholders (?) via sqlite3 — no query string is ever built by concatenating user input.
