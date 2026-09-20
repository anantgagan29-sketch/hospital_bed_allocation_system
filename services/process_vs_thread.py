"""
Process vs Thread demonstration.

Runs the identical small workload — a stand-in for "check + prepare an
allocation decision" — once with worker threads and once with worker
processes, and reports what actually differs: memory sharing and
measured wall-clock time on THIS machine. No claim is made about exact
Linux kernel scheduling behaviour; only what was observed.
"""
import multiprocessing
import threading
import time
from typing import List


def _simulated_allocation_check(n: int) -> int:
    """CPU-bound busy work standing in for a bed-availability computation."""
    total = 0
    for i in range(n):
        total += i * i
    return total


def _run_with_threads(num_workers: int, workload: int) -> dict:
    shared_results: List[int] = []
    results_lock = threading.Lock()

    def worker():
        value = _simulated_allocation_check(workload)
        with results_lock:
            shared_results.append(value)

    start = time.perf_counter()
    threads = [threading.Thread(target=worker) for _ in range(num_workers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start

    return {
        "mode": "THREAD",
        "workers": num_workers,
        "elapsed_ms": round(elapsed * 1000, 3),
        "results_collected": len(shared_results),
        "memory_model": "Shared — all threads read/write the same process memory (needs locks for shared state).",
    }


def _process_worker(workload: int, output_queue: multiprocessing.Queue) -> None:
    output_queue.put(_simulated_allocation_check(workload))


def _run_with_processes(num_workers: int, workload: int) -> dict:
    output_queue = multiprocessing.Queue()
    start = time.perf_counter()
    processes = [
        multiprocessing.Process(target=_process_worker, args=(workload, output_queue))
        for _ in range(num_workers)
    ]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    elapsed = time.perf_counter() - start

    collected = []
    while not output_queue.empty():
        collected.append(output_queue.get())

    return {
        "mode": "PROCESS",
        "workers": num_workers,
        "elapsed_ms": round(elapsed * 1000, 3),
        "results_collected": len(collected),
        "memory_model": "Isolated — each process has its own memory space; results must be sent back "
                         "explicitly (here, via a multiprocessing.Queue).",
    }


def compare(num_workers: int = 4, workload: int = 2_000_000) -> dict:
    thread_result = _run_with_threads(num_workers, workload)
    process_result = _run_with_processes(num_workers, workload)
    return {
        "workload_units": workload,
        "thread": thread_result,
        "process": process_result,
    }
