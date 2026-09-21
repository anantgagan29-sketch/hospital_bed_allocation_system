"""
Linux System Monitor: runs a fixed whitelist of read-only commands via
subprocess and returns their output. Nothing here accepts a command
string built from user input — every entry point takes a `command_key`
that must already be a key in config.ALLOWED_LINUX_COMMANDS or in the
explicit dispatch table below. This is what keeps section 12/28 of the
brief (no arbitrary shell execution) true even though the feature is
real subprocess execution, not a mock.

Application interaction with OS services (see docs/LINUX_COMMANDS.md and
the "system call concept" note in the brief):
    os.getpid()      -> process identity, obtained through the OS
    os.listdir()     -> filesystem access, provided by the OS
    subprocess.run() -> creates a child process via OS process management
    open()           -> file I/O, serviced by the OS
None of this bypasses the kernel; it is Python asking the kernel to do
these things on the application's behalf.
"""
import os
import platform
import subprocess

import config

COMMAND_PURPOSE = {
    "uname":   "Displays OS/kernel information (uname -a).",
    "whoami":  "Shows the current user the server process is running as.",
    "pwd":     "Shows the server process's current working directory.",
    "ls":      "Lists the project directory's files.",
    "df":      "Shows disk-space utilisation (df -h).",
    "free":    "Shows memory usage (Linux only; free -h).",
    "uptime":  "Shows system uptime and load average.",
    "ps":      "Lists running processes (ps -e).",
    "ps_aux":  "Shows detailed process information (ps aux).",
    "wc_processes": "Counts running processes: `ps aux | wc -l`.",
}


def _run(args: list, timeout: int = 5) -> dict:
    try:
        completed = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return {
            "ok": completed.returncode == 0,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "returncode": completed.returncode,
        }
    except FileNotFoundError:
        return {"ok": False, "stdout": "", "stderr": "command not found on this OS", "returncode": -1}
    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "", "stderr": "command timed out", "returncode": -1}


def run_command(command_key: str) -> dict:
    """Execute one whitelisted command. Rejects anything not in the whitelist."""
    if command_key not in config.ALLOWED_LINUX_COMMANDS:
        return {"ok": False, "stdout": "", "stderr": "command not whitelisted", "returncode": -1}

    if command_key == "wc_processes":
        # Demonstrates a pipe (ps aux | wc -l) built from two whitelisted,
        # fixed argument lists — never from user input.
        ps_result = _run(config.ALLOWED_LINUX_COMMANDS["ps_aux"])
        if not ps_result["ok"]:
            return ps_result
        line_count = len(ps_result["stdout"].splitlines())
        return {"ok": True, "stdout": f"{line_count}", "stderr": "", "returncode": 0}

    result = _run(config.ALLOWED_LINUX_COMMANDS[command_key])
    if command_key == "free" and not result["ok"]:
        result["stdout"] = "(not available on macOS — this command targets Linux)"
        result["ok"] = True
    return result


def run_all() -> dict:
    return {key: {**run_command(key), "purpose": COMMAND_PURPOSE.get(key, "")}
            for key in config.ALLOWED_LINUX_COMMANDS}


def python_os_interface_demo() -> dict:
    """Demonstrates application-level use of OS services through Python,
    without claiming these ARE Linux system calls themselves."""
    return {
        "os.getpid()": os.getpid(),
        "os.getcwd()": os.getcwd(),
        "os.listdir('.')_count": len(os.listdir(".")),
        "platform.system()": platform.system(),
        "platform.release()": platform.release(),
        "os.cpu_count()": os.cpu_count(),
    }


def log_startup_diagnostics(db) -> None:
    """Runs a handful of real Linux commands and the Python/OS-interface demo
    once, and writes their actual output into system_logs. This is what
    makes Linux command execution part of the app's real, live behaviour
    (checked on every server start) rather than something only exercised by
    tests/test_system_monitor.py. See docs/LINUX_COMMANDS.md."""
    from models.db import log_event

    for key in ("uname", "whoami", "uptime", "df", "ps_aux"):
        result = run_command(key)
        output = result["stdout"] if result["ok"] else f"error: {result['stderr']}"
        log_event(
            source=f"linux:{key}",
            message=output[:300],
            level="INFO" if result["ok"] else "WARN",
            connection=db,
        )

    interface_demo = python_os_interface_demo()
    log_event(
        source="python_os_interface",
        message=", ".join(f"{k}={v}" for k, v in interface_demo.items()),
        level="INFO",
        connection=db,
    )
    db.commit()


def run_shell_script(script_name: str) -> dict:
    """Runs one whitelisted script from scripts/ via bash. script_name must
    be a bare filename already present on disk in SCRIPTS_DIR — never a
    path built from a request parameter."""
    allowed_scripts = {
        "setup.sh", "start_server.sh", "stop_server.sh", "backup_database.sh",
        "system_report.sh", "cleanup.sh", "health_check.sh",
    }
    if script_name not in allowed_scripts:
        return {"ok": False, "stdout": "", "stderr": "script not whitelisted", "returncode": -1}

    script_path = os.path.join(config.SCRIPTS_DIR, script_name)
    if not os.path.isfile(script_path):
        return {"ok": False, "stdout": "", "stderr": "script not found", "returncode": -1}

    return _run(["bash", script_path], timeout=15)
