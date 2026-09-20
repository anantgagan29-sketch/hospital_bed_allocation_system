"""Integration tests against a real (in-memory) SQLite schema (TC01, TC03-TC05)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import fresh_db

from models import beds as bed_model
from models import patients as patient_model
from models import requests as request_model
from services import allocation_service, scheduler


class AllocationServiceTests(unittest.TestCase):
    def setUp(self):
        self.db = fresh_db()

    def tearDown(self):
        self.db.close()

    def _add_bed(self, bed_id, bed_type="ICU"):
        self.db.execute("INSERT INTO beds (bed_id, ward, type, status) VALUES (?, 'Ward', ?, 'AVAILABLE')",
                         (bed_id, bed_type))
        self.db.commit()

    def _add_patient(self, name="Test Patient"):
        return patient_model.create_patient(self.db, name, 40, "M", "Test condition", "0000000000")

    def _add_request(self, patient_id, patient_name, urgency, bed_type="ICU", burst=5):
        return request_model.create_request(self.db, patient_id, patient_name, 40, "Test",
                                              urgency, bed_type, burst)

    def test_tc01_two_requests_one_bed(self):
        self._add_bed("ICU-01")
        p1 = self._add_patient("Alpha")
        p2 = self._add_patient("Beta")
        self._add_request(p1, "Alpha", "MEDIUM")
        self._add_request(p2, "Beta", "MEDIUM")

        result = scheduler.run(self.db, "FCFS")
        outcomes = allocation_service.execute_schedule(self.db, result)

        allocated = [o for o in outcomes if o["allocated"]]
        waiting = [o for o in outcomes if not o["allocated"]]
        self.assertEqual(len(allocated), 1)
        self.assertEqual(len(waiting), 1)

    def test_tc03_critical_beats_low_priority(self):
        # Both requests are ALREADY pending together (same arrival_time) when
        # Run Scheduler is clicked -- the realistic case, since Priority
        # scheduling is non-preemptive: it can only reorder among requests
        # that have already arrived by the time the engine looks at the
        # queue. (A low-priority request that arrives alone, before a
        # critical one is even submitted, legitimately runs first -- see
        # docs/SCHEDULING.md "Why arrival order still matters".)
        self._add_bed("ICU-01")
        p_low = self._add_patient("Low Urgency")
        p_critical = self._add_patient("Critical Case")
        self.db.execute(
            """INSERT INTO allocation_requests
               (request_id, patient_id, patient_name, age, medical_condition, urgency,
                required_bed_type, arrival_time, burst_time, priority, status)
               VALUES ('REQ-LOW', ?, 'Low Urgency', 40, 'Test', 'LOW', 'ICU', 1, 5, 4, 'PENDING')""",
            (p_low,),
        )
        self.db.execute(
            """INSERT INTO allocation_requests
               (request_id, patient_id, patient_name, age, medical_condition, urgency,
                required_bed_type, arrival_time, burst_time, priority, status)
               VALUES ('REQ-CRIT', ?, 'Critical Case', 40, 'Test', 'CRITICAL', 'ICU', 1, 5, 1, 'PENDING')""",
            (p_critical,),
        )
        self.db.commit()

        result = scheduler.run(self.db, "PRIORITY")
        outcomes = allocation_service.execute_schedule(self.db, result)

        winner = next(o for o in outcomes if o["allocated"])
        self.assertEqual(winner["patient_name"], "Critical Case")

    def test_tc04_no_beds_available(self):
        # No beds inserted at all.
        p1 = self._add_patient("Nobody")
        self._add_request(p1, "Nobody", "HIGH")

        result = scheduler.run(self.db, "FCFS")
        outcomes = allocation_service.execute_schedule(self.db, result)

        self.assertFalse(outcomes[0]["allocated"])
        row = request_model.get_request(self.db, outcomes[0]["request_id"])
        self.assertEqual(row["status"], "WAITING")

    def test_tc05_discharge_frees_bed_for_waiting_request(self):
        self._add_bed("ICU-01")
        p1 = self._add_patient("First")
        p2 = self._add_patient("Second")
        self._add_request(p1, "First", "HIGH")
        self._add_request(p2, "Second", "HIGH")

        result = scheduler.run(self.db, "FCFS")
        allocation_service.execute_schedule(self.db, result)

        bed = bed_model.get_bed(self.db, "ICU-01")
        self.assertEqual(bed["status"], "ALLOCATED")

        outcome = allocation_service.discharge(self.db, "ICU-01")
        self.assertTrue(outcome["released"])
        self.assertEqual(outcome["reallocated_to"], "Second")

        bed = bed_model.get_bed(self.db, "ICU-01")
        self.assertEqual(bed["status"], "ALLOCATED")


if __name__ == "__main__":
    unittest.main()
