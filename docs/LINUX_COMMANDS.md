# Linux Commands Used In This Project

All commands below are run through `services/system_monitor.py::run_command()`,
which only ever executes an entry from the fixed whitelist in
`config.ALLOWED_LINUX_COMMANDS` — never a string built from user input.

| Command | Purpose | Where it's used |
|---|---|---|
| `uname -a` | Displays OS/kernel information (kernel name, version, architecture). | `/linux-monitor` |
| `whoami` | Shows the user the server process is running as. | `/linux-monitor` |
| `pwd` | Shows the server's current working directory. | `/linux-monitor` |
| `ls -la` | Lists the project directory's files. | `/linux-monitor` |
| `df -h` | Shows disk-space utilisation in human-readable form. | `/linux-monitor`, `scripts/system_report.sh` |
| `free -h` | Shows memory usage (Linux-only; the app reports gracefully on macOS). | `/linux-monitor`, `scripts/system_report.sh` |
| `uptime` | Shows system uptime and load average. | `/linux-monitor`, `scripts/system_report.sh` |
| `ps -e` / `ps aux` | Lists running processes / detailed process info. | `/linux-monitor`, `scripts/system_report.sh` |
| `ps aux \| wc -l` | Counts running processes (built from two whitelisted, fixed calls — never a shell string from user input). | `/linux-monitor` |

## Why a whitelist instead of a free-text command box

Accepting an arbitrary command string from a web form and running it
through a shell is a classic command-injection vulnerability (OWASP
Top 10). Instead:

- Every runnable command is a **fixed Python list** of arguments
  (`["uname", "-a"]`), defined once in `config.py`.
- `subprocess.run(args, capture_output=True, text=True, timeout=5)` is
  called with that fixed list — `shell=True` is never used, so shell
  metacharacters in any (nonexistent) user input could never matter anyway.
- `run_command()` and `run_shell_script()` both reject any key/filename
  that isn't already in their whitelist, returning an error instead of
  executing anything.

## Shell scripting concepts demonstrated (scripts/)

- **Shell variables:** `PROJECT_DIR`, `TIMESTAMP`, `STATUS_CODE`, etc.
- **Redirection:** `system_report.sh` uses `{ ... } > reports/system_report.txt`.
- **Pipes:** `ps aux | wc -l` inside `system_report.sh`.
- **Exit codes:** `set -e` in every script stops it on the first failing
  command; `health_check.sh` explicitly `exit 0`/`exit 1` based on the
  HTTP status it observes.
- **Conditionals:** `if [ -f "venv/bin/activate" ]; then ...` style checks
  before acting, so scripts degrade gracefully instead of crashing.
- **`chmod +x`:** required before any of these scripts can run as
  `./scripts/name.sh` instead of `bash scripts/name.sh` — it sets the
  execute permission bit the OS checks before running a file directly.

## Application-level OS interaction (not real system calls)

`services/system_monitor.py::python_os_interface_demo()` shows four
examples of Python asking the OS to do something, without claiming these
ARE Linux system calls themselves:

- `os.getpid()` — obtains process identity through the OS.
- `os.listdir('.')` — accesses filesystem resources.
- `subprocess.run()` — creates a child process via OS process management.
- `open()` (used throughout `models/db.py` indirectly via SQLite) — file
  I/O serviced by the OS.
