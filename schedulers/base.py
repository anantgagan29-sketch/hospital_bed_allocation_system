"""
Shared types and metric formulas used by every scheduling algorithm.

IMPORTANT (see docs/SCHEDULING.md): this simulates CPU-style scheduling
at the application level, over allocation requests standing in for
processes. It does not touch the real Linux CPU scheduler.

Formulas (standard OS definitions):
    Waiting Time    = Turnaround Time - Burst Time
    Turnaround Time = Completion Time - Arrival Time
    Response Time   = First Start Time - Arrival Time
    Throughput      = Completed Processes / Total Execution Time
"""
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SchedProcess:
    """Minimal process record a scheduler operates on. Mirrors a PCB row."""
    pid: int
    request_id: str
    patient_name: str
    arrival_time: int
    burst_time: int
    priority: int  # lower number = higher priority (CRITICAL=1 ... LOW=4)


@dataclass
class GanttBlock:
    pid: int
    patient_name: str
    start: int
    end: int


@dataclass
class ScheduleResult:
    algorithm: str
    order: List[int]                 # pids in the order they finished
    gantt: List[GanttBlock]
    per_process: List[Dict]          # one dict per process with all metrics
    averages: Dict[str, float]
    throughput: float
    total_time: int


def merge_gantt(raw_blocks: List[GanttBlock]) -> List[GanttBlock]:
    """Collapse consecutive blocks of the same pid (produced by time-stepping
    simulations like SRTF/Round Robin) into single contiguous bars."""
    if not raw_blocks:
        return []
    merged = [raw_blocks[0]]
    for block in raw_blocks[1:]:
        last = merged[-1]
        if block.pid == last.pid and block.start == last.end:
            last.end = block.end
        else:
            merged.append(block)
    return merged


def build_result(algorithm: str, processes: List[SchedProcess], gantt: List[GanttBlock],
                  first_start: Dict[int, int], completion: Dict[int, int]) -> ScheduleResult:
    per_process = []
    for p in processes:
        turnaround = completion[p.pid] - p.arrival_time
        waiting = turnaround - p.burst_time
        response = first_start[p.pid] - p.arrival_time
        per_process.append({
            "pid": p.pid,
            "request_id": p.request_id,
            "patient_name": p.patient_name,
            "priority": p.priority,
            "arrival_time": p.arrival_time,
            "burst_time": p.burst_time,
            "start_time": first_start[p.pid],
            "completion_time": completion[p.pid],
            "waiting_time": waiting,
            "turnaround_time": turnaround,
            "response_time": response,
        })

    n = len(per_process)
    avg_waiting = sum(pp["waiting_time"] for pp in per_process) / n
    avg_turnaround = sum(pp["turnaround_time"] for pp in per_process) / n
    avg_response = sum(pp["response_time"] for pp in per_process) / n

    earliest_arrival = min(p.arrival_time for p in processes)
    latest_completion = max(completion.values())
    total_time = max(latest_completion - earliest_arrival, 1)
    throughput = round(n / total_time, 4)

    order = sorted(completion, key=completion.get)

    return ScheduleResult(
        algorithm=algorithm,
        order=order,
        gantt=gantt,
        per_process=sorted(per_process, key=lambda pp: pp["completion_time"]),
        averages={
            "waiting_time": round(avg_waiting, 2),
            "turnaround_time": round(avg_turnaround, 2),
            "response_time": round(avg_response, 2),
        },
        throughput=throughput,
        total_time=total_time,
    )
