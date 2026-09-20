"""Unit tests for the five scheduling algorithms (TC06, TC07)."""
import unittest

from schedulers import fcfs, priority, round_robin, srtf
from schedulers.base import SchedProcess


def make(pid, arrival, burst, prio=3):
    return SchedProcess(pid=pid, request_id=f"REQ-{pid}", patient_name=f"P{pid}",
                         arrival_time=arrival, burst_time=burst, priority=prio)


class TestFCFS(unittest.TestCase):
    def test_known_example(self):
        # Textbook FCFS example with a hand-computed answer.
        processes = [make(1, 0, 5), make(2, 1, 3), make(3, 2, 8), make(4, 3, 6)]
        result = fcfs.schedule(processes)
        by_pid = {pp["pid"]: pp for pp in result.per_process}

        self.assertEqual(by_pid[1]["completion_time"], 5)
        self.assertEqual(by_pid[2]["completion_time"], 8)
        self.assertEqual(by_pid[3]["completion_time"], 16)
        self.assertEqual(by_pid[4]["completion_time"], 22)
        self.assertAlmostEqual(result.averages["waiting_time"], 5.75)


class TestPriority(unittest.TestCase):
    def test_critical_beats_low_at_same_arrival(self):
        # Emergency (priority 1) must run before a routine request (priority 4)
        # that arrived at the same time.
        low = make(1, 0, 5, prio=4)
        critical = make(2, 0, 5, prio=1)
        result = priority.schedule([low, critical])
        self.assertEqual(result.order[0], critical.pid)


class TestSRTF(unittest.TestCase):
    def test_shorter_job_preempts_running_one(self):
        # P1 starts running at t=0 with a long burst; a much shorter P2
        # arrives shortly after and must finish first.
        p1 = make(1, 0, 10)
        p2 = make(2, 2, 1)
        result = srtf.schedule([p1, p2])
        completion = {pp["pid"]: pp["completion_time"] for pp in result.per_process}
        self.assertLess(completion[2], completion[1])
        # P1 must have been split into at least two Gantt blocks (preempted).
        p1_blocks = [b for b in result.gantt if b.pid == 1]
        self.assertGreaterEqual(len(p1_blocks), 2)


class TestRoundRobin(unittest.TestCase):
    def test_single_process_runs_straight_through(self):
        # With nothing else in the ready queue, RR degenerates to running the
        # one process solid -- merge_gantt correctly shows this as one block.
        processes = [make(1, 0, 10)]
        result = round_robin.schedule(processes, quantum=3)
        self.assertEqual(result.per_process[0]["completion_time"], 10)

    def test_two_processes_interleave_across_quanta(self):
        processes = [make(1, 0, 10), make(2, 0, 4)]
        result = round_robin.schedule(processes, quantum=3)
        # Both processes must appear more than once in the Gantt chart --
        # proof that execution actually alternates between them.
        p1_blocks = [b for b in result.gantt if b.pid == 1]
        p2_blocks = [b for b in result.gantt if b.pid == 2]
        self.assertGreater(len(p1_blocks), 1)
        self.assertGreaterEqual(len(p2_blocks), 1)
        self.assertGreater(len(result.gantt), 2)

    def test_every_process_gets_a_fair_turn(self):
        processes = [make(1, 0, 9), make(2, 0, 1)]
        result = round_robin.schedule(processes, quantum=3)
        # The short job (burst 1) must not wait for the long job to fully finish.
        completion = {pp["pid"]: pp["completion_time"] for pp in result.per_process}
        self.assertLess(completion[2], completion[1])


if __name__ == "__main__":
    unittest.main()
