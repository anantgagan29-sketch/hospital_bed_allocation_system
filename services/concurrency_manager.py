"""
Concurrency & Race Condition Demo.

Runs on an isolated, in-memory pool of "demo beds" — never the real
hospital data — so it can be re-run any number of times during a viva
without disturbing the live dashboard. See docs/CONCURRENCY.md for the
full explanation of why the lock is necessary.

The critical section every thread executes is exactly the one described
in the assignment brief:

    CHECK AVAILABLE BED -> SELECT BED -> ALLOCATE BED -> UPDATE STATE

A short artificial delay (time.sleep) is inserted between "check" and
"allocate" to reliably widen the race window — real allocations are fast
enough that two threads rarely collide by chance, but the underlying bug
is identical regardless of timing.
"""
import threading
import time
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class DemoBed:
    bed_id: str
    available: bool = True


class RaceConditionDemo:
    def __init__(self, num_beds: int, num_threads: int, use_lock: bool, delay_seconds: float = 0.01):
        self.beds = [DemoBed(f"DEMO-{i + 1}") for i in range(num_beds)]
        self.num_threads = num_threads
        self.use_lock = use_lock
        self.delay_seconds = delay_seconds
        self.lock = threading.Lock()
        self._events_lock = threading.Lock()
        self.events: List[str] = []
        self.successful: List[Tuple[int, str]] = []
        self.waiting: List[int] = []

    def _log(self, message: str) -> None:
        with self._events_lock:
            self.events.append(message)

    def _find_available(self):
        for bed in self.beds:
            if bed.available:
                return bed
        return None

    def _critical_section(self, thread_id: int) -> None:
        bed = self._find_available()                      # CHECK
        if bed is None:
            self._log(f"Thread-{thread_id}: no demo bed available -> request WAITING")
            with self._events_lock:
                self.waiting.append(thread_id)
            return

        self._log(f"Thread-{thread_id}: sees {bed.bed_id} as available, preparing to allocate")
        time.sleep(self.delay_seconds)                     # window where a race can happen
        bed.available = False                              # ALLOCATE (no re-check: unsafe on purpose)
        self._log(f"Thread-{thread_id}: allocated {bed.bed_id}")
        with self._events_lock:
            self.successful.append((thread_id, bed.bed_id))

    def _attempt(self, thread_id: int) -> None:
        if self.use_lock:
            self._log(f"Thread-{thread_id}: waiting for lock...")
            with self.lock:
                self._log(f"Thread-{thread_id}: acquired lock, entering critical section")
                self._critical_section(thread_id)
                self._log(f"Thread-{thread_id}: released lock")
        else:
            self._critical_section(thread_id)

    def run(self) -> dict:
        start = time.perf_counter()
        threads = [threading.Thread(target=self._attempt, args=(i + 1,)) for i in range(self.num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed_ms = round((time.perf_counter() - start) * 1000, 3)

        bed_ids_given_out = [bed_id for _, bed_id in self.successful]
        unique_beds = set(bed_ids_given_out)
        conflicts = len(bed_ids_given_out) - len(unique_beds)

        return {
            "lock_used": self.use_lock,
            "num_threads": self.num_threads,
            "num_beds": len(self.beds),
            "successful_attempts": len(self.successful),
            "unique_beds_allocated": len(unique_beds),
            "conflicting_allocations": conflicts,
            "waiting_requests": len(self.waiting),
            "execution_time_ms": elapsed_ms,
            "events": self.events,
            "is_safe": conflicts == 0,
        }


def run_demo(num_beds: int, num_threads: int, use_lock: bool) -> dict:
    demo = RaceConditionDemo(num_beds=num_beds, num_threads=num_threads, use_lock=use_lock)
    return demo.run()
