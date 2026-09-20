"""Race-condition demo tests (TC02, TC08)."""
import unittest

from services.concurrency_manager import RaceConditionDemo


class ConcurrencyTests(unittest.TestCase):
    def test_tc08_lock_prevents_conflicting_allocations(self):
        demo = RaceConditionDemo(num_beds=1, num_threads=10, use_lock=True)
        result = demo.run()
        self.assertEqual(result["conflicting_allocations"], 0)
        self.assertEqual(result["successful_attempts"], 1)
        self.assertEqual(result["waiting_requests"], 9)
        self.assertTrue(result["is_safe"])

    def test_tc02_without_lock_two_threads_same_bed_can_conflict(self):
        demo = RaceConditionDemo(num_beds=1, num_threads=10, use_lock=False)
        result = demo.run()
        self.assertGreater(result["conflicting_allocations"], 0)
        self.assertFalse(result["is_safe"])

    def test_lock_never_exceeds_bed_capacity(self):
        for _ in range(5):
            demo = RaceConditionDemo(num_beds=3, num_threads=12, use_lock=True)
            result = demo.run()
            self.assertLessEqual(result["unique_beds_allocated"], 3)
            self.assertEqual(result["conflicting_allocations"], 0)


if __name__ == "__main__":
    unittest.main()
