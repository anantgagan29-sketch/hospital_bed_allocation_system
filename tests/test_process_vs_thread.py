"""Process vs Thread comparison — not wired to a page, but runs internally
and is verified here so the underlying OS concept stays proven to work."""
import unittest

from services import process_vs_thread


class ProcessVsThreadTests(unittest.TestCase):
    def test_both_modes_complete_and_report_results(self):
        comparison = process_vs_thread.compare(num_workers=2, workload=50_000)
        self.assertEqual(comparison["thread"]["results_collected"], 2)
        self.assertEqual(comparison["process"]["results_collected"], 2)
        self.assertIn("Shared", comparison["thread"]["memory_model"])
        self.assertIn("Isolated", comparison["process"]["memory_model"])


if __name__ == "__main__":
    unittest.main()
