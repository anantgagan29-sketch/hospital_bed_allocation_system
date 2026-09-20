# CPU Scheduling in This Project

## What is actually being scheduled

Not the CPU itself — **allocation requests**, modeled as processes with
`arrival_time`, `burst_time` and `priority`. The scheduler decides the
ORDER in which `services/allocation_service.py` should attempt a real bed
allocation for each request. See the pipeline:

```
REQUEST QUEUE -> SCHEDULER -> RESOURCE CHECK -> BED ALLOCATION -> COMPLETION
```

`burst_time` is an abstract "estimated allocation-processing time" chosen
when the request is created — **not** the patient's real length of stay.

## Formulas (standard OS definitions, `schedulers/base.py::build_result`)

```
Waiting Time    = Turnaround Time - Burst Time
Turnaround Time = Completion Time - Arrival Time
Response Time   = First Start Time - Arrival Time
Throughput      = Completed Processes / Total Execution Time
```

## The five algorithms

| Algorithm | File | Preemptive? | Selection rule |
|---|---|---|---|
| FCFS | `schedulers/fcfs.py` | No | Strict arrival-time order |
| SJF | `schedulers/sjf.py` | No | Smallest `burst_time` among arrived requests |
| SRTF | `schedulers/srtf.py` | **Yes** | Smallest *remaining* burst time, re-checked every time unit |
| Priority | `schedulers/priority.py` | No | Smallest priority number (CRITICAL=1 ... LOW=4) among arrived requests |
| Round Robin | `schedulers/round_robin.py` | Time-sliced | Each ready request gets at most `quantum` units per turn, then goes to the back of the queue if unfinished |

## Why arrival order still matters under Priority/SJF

Priority and SJF here are **non-preemptive**: once a request starts
running, the scheduler will not interrupt it just because a more urgent
request shows up. Concretely, the very first request the engine looks at
(whichever has the smallest `arrival_time`) is *always* the one it starts
with — there is nothing else in the "arrived" set yet, regardless of its
priority. Only **SRTF** is preemptive and can hand the resource to a
just-arrived request with a shorter remaining burst.

This is standard, textbook-correct non-preemptive scheduling behaviour —
not a bug — and it is exactly why real-world priority scheduling still
needs *some* preemption or fast-tracking mechanism (e.g. paging an
emergency team) for truly time-critical cases. It is one of the strongest
viva talking points this project has: *"why doesn't Priority Scheduling
always let the critical patient in first?"*

`tests/test_allocation_service.py::test_tc03_critical_beats_low_priority`
demonstrates the *correct* case: when both requests are already pending
together (the realistic scenario when an admin clicks "Run Scheduler"
after creating several requests), Priority correctly picks the critical
one first.

## Round Robin's time quantum

`config.DEFAULT_TIME_QUANTUM = 4` (overridable per run). A process that
doesn't finish within its quantum goes to the back of the ready queue.
With only one process in the queue, Round Robin degenerates to running it
solid (there's nothing to round-robin with) — `merge_gantt()` in
`schedulers/base.py` correctly collapses consecutive same-process turns
into one visual Gantt block.

## Scheduling Metrics page

`/scheduling-metrics` (`services/scheduler.py::compare_all`) runs **all
five algorithms against the identical pending-request snapshot** — a fair,
apples-to-apples comparison of average waiting/turnaround/response time
and throughput. This calculation never touches real bed data; only
**Run & Allocate** on the Scheduler page does that.

## What this is NOT

This does not control, replace, or bypass the real Linux CPU scheduler.
Flask, Python and every thread this app creates are still scheduled by
the actual kernel exactly as normal — see `docs/OS_CONCEPT_MAPPING.md`.
