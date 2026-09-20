"""Shortest Job First: non-preemptive. Among arrived requests, run the one
with the smallest burst_time (estimated allocation-processing time) next."""
from typing import List

from schedulers.base import SchedProcess, GanttBlock, ScheduleResult, build_result


def schedule(processes: List[SchedProcess]) -> ScheduleResult:
    remaining = sorted(processes, key=lambda p: (p.arrival_time, p.pid))
    gantt = []
    first_start = {}
    completion = {}
    clock = remaining[0].arrival_time

    pending = list(remaining)
    while pending:
        arrived = [p for p in pending if p.arrival_time <= clock]
        if not arrived:
            clock = min(p.arrival_time for p in pending)
            continue

        next_p = min(arrived, key=lambda p: (p.burst_time, p.arrival_time, p.pid))
        start = clock
        end = start + next_p.burst_time
        gantt.append(GanttBlock(next_p.pid, next_p.patient_name, start, end))
        first_start[next_p.pid] = start
        completion[next_p.pid] = end
        clock = end
        pending.remove(next_p)

    return build_result("SJF", processes, gantt, first_start, completion)
