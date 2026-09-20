"""First-Come, First-Served scheduling: processed strictly in arrival order."""
from typing import List

from schedulers.base import SchedProcess, GanttBlock, ScheduleResult, build_result


def schedule(processes: List[SchedProcess]) -> ScheduleResult:
    ordered = sorted(processes, key=lambda p: (p.arrival_time, p.pid))

    gantt = []
    first_start = {}
    completion = {}
    clock = ordered[0].arrival_time

    for p in ordered:
        start = max(clock, p.arrival_time)
        end = start + p.burst_time
        gantt.append(GanttBlock(p.pid, p.patient_name, start, end))
        first_start[p.pid] = start
        completion[p.pid] = end
        clock = end

    return build_result("FCFS", processes, gantt, first_start, completion)
