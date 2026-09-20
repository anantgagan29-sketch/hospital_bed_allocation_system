"""Linux command / shell script whitelist tests (TC09, TC10)."""
import unittest

from services import system_monitor


class SystemMonitorTests(unittest.TestCase):
    def test_tc09_whitelisted_command_runs(self):
        result = system_monitor.run_command("whoami")
        self.assertTrue(result["ok"])
        self.assertTrue(result["stdout"])

    def test_tc09_non_whitelisted_command_rejected(self):
        result = system_monitor.run_command("rm -rf /")
        self.assertFalse(result["ok"])
        self.assertEqual(result["stderr"], "command not whitelisted")

    def test_tc10_whitelisted_script_runs(self):
        result = system_monitor.run_shell_script("system_report.sh")
        self.assertTrue(result["ok"])

    def test_tc10_non_whitelisted_script_rejected(self):
        result = system_monitor.run_shell_script("../../etc/passwd")
        self.assertFalse(result["ok"])
        self.assertEqual(result["stderr"], "script not whitelisted")


if __name__ == "__main__":
    unittest.main()
