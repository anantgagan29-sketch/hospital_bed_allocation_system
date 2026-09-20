"""Round Robin: each request gets at most `quantum` time units per turn,
then goes to the back of the ready queue if it isn't finished."""
from collections import deque
from typing import List

import config
from schedulers.base import SchedProcess, GanttBlock, ScheduleResult, build_result, merge_gantt


def schedule(processes: List[SchedProcess], quantum: int = None) -> ScheduleResult:
    quantum = quantum or config.DEFAULT_TIME_QUANTUM
    remaining_time = {p.pid: p.burst_time for p in processes}
    first_start = {}
    completion = {}
    raw_gantt = []

    arrivals = sorted(processes, key=lambda p: (p.arrival_time, p.pid))
    clock = arrivals[0].arrival_time
    queue = deque()
    not_yet_arrived = deque(arrivals)

    def admit_arrivals(up_to_time: int) -> None:
        while not_yet_arrived and not_yet_arrived[0].arrival_time <= up_to_time:
            queue.append(not_yet_arrived.popleft())

    admit_arrivals(clock)

    while queue or not_yet_arrived:
        if not queue:
            clock = not_yet_arrived[0].arrival_time
            admit_arrivals(clock)
            continue

        current = queue.popleft()
        if current.pid not in first_start:
            first_start[current.pid] = clock

        run_for = min(quantum, remaining_time[current.pid])
        start = clock
        end = clock + run_for
        raw_gantt.append(GanttBlock(current.pid, current.patient_name, start, end))

        remaining_time[current.pid] -= run_for
        clock = end
        admit_arrivals(clock)

        if remaining_time[current.pid] > 0:
            queue.append(current)
        else:
            completion[current.pid] = clock

    gantt = merge_gantt(raw_gantt)
    return build_result("Round Robin", processes, gantt, first_start, completion)
