"""Shortest Remaining Time First: preemptive version of SJF. At every time
unit, the request with the least remaining burst time gets the resource."""
from typing import List

from schedulers.base import SchedProcess, GanttBlock, ScheduleResult, build_result, merge_gantt


def schedule(processes: List[SchedProcess]) -> ScheduleResult:
    remaining_time = {p.pid: p.burst_time for p in processes}
    first_start = {}
    completion = {}
    raw_gantt = []

    clock = min(p.arrival_time for p in processes)
    total_burst = sum(p.burst_time for p in processes)
    end_clock = clock + total_burst
    by_pid = {p.pid: p for p in processes}

    while len(completion) < len(processes) and clock < end_clock:
        arrived = [p for p in processes if p.arrival_time <= clock and remaining_time[p.pid] > 0]
        if not arrived:
            clock += 1
            continue

        current = min(arrived, key=lambda p: (remaining_time[p.pid], p.arrival_time, p.pid))
        if current.pid not in first_start:
            first_start[current.pid] = clock

        raw_gantt.append(GanttBlock(current.pid, current.patient_name, clock, clock + 1))
        remaining_time[current.pid] -= 1
        clock += 1

        if remaining_time[current.pid] == 0:
            completion[current.pid] = clock

    gantt = merge_gantt(raw_gantt)
    return build_result("SRTF", processes, gantt, first_start, completion)
