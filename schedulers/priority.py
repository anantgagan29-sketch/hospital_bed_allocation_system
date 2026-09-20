"""Priority scheduling: non-preemptive. Lower priority number = more urgent
(CRITICAL=1 ... LOW=4), matching config.URGENCY_PRIORITY. This is how
emergency patients jump the queue ahead of routine ones."""
from typing import List

from schedulers.base import SchedProcess, GanttBlock, ScheduleResult, build_result


def schedule(processes: List[SchedProcess]) -> ScheduleResult:
    gantt = []
    first_start = {}
    completion = {}
    clock = min(p.arrival_time for p in processes)

    pending = list(processes)
    while pending:
        arrived = [p for p in pending if p.arrival_time <= clock]
        if not arrived:
            clock = min(p.arrival_time for p in pending)
            continue

        next_p = min(arrived, key=lambda p: (p.priority, p.arrival_time, p.pid))
        start = clock
        end = start + next_p.burst_time
        gantt.append(GanttBlock(next_p.pid, next_p.patient_name, start, end))
        first_start[next_p.pid] = start
        completion[next_p.pid] = end
        clock = end
        pending.remove(next_p)

    return build_result("Priority", processes, gantt, first_start, completion)
