"""
Application configuration.

Kept as plain constants (no framework-specific config class) because this
project intentionally avoids unnecessary abstraction — see docs/PROJECT_ARCHITECTURE.md.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
SEED_PATH = os.path.join(BASE_DIR, "database", "seed_data.sql")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

# On Vercel (and most serverless hosts), everything except /tmp is a
# read-only filesystem, and /tmp itself is wiped on every cold start. A real
# server deployment (Render, Railway, PythonAnywhere, your own machine) has
# a normal writable disk, so the database survives restarts there. On
# Vercel it does not: expect demo data to reset whenever a new container
# spins up. See docs/DEPLOYMENT.md.
if os.environ.get("VERCEL") == "1":
    DATABASE_PATH = "/tmp/hospital.db"
else:
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "hospital.db")

SECRET_KEY = os.environ.get("HOSPITAL_APP_SECRET", "os-pbl-dev-secret-key")

# Round Robin scheduling quantum (in the same abstract time unit as burst_time)
DEFAULT_TIME_QUANTUM = 4

# Urgency -> numeric priority. Lower number = higher priority (matches OS convention).
URGENCY_PRIORITY = {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4,
}

BED_TYPES = ["ICU", "GENERAL", "EMERGENCY", "PEDIATRIC", "ISOLATION"]
BED_STATUSES = ["AVAILABLE", "ALLOCATED", "MAINTENANCE"]
URGENCY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
REQUEST_STATUSES = ["PENDING", "IN_PROGRESS", "ALLOCATED", "WAITING", "REJECTED"]
PROCESS_STATES = ["NEW", "READY", "RUNNING", "WAITING", "BLOCKED", "TERMINATED"]

# Whitelisted read-only Linux commands for the Linux System Monitor.
# Nothing outside this map can ever be executed via the web UI.
ALLOWED_LINUX_COMMANDS = {
    "uname": ["uname", "-a"],
    "whoami": ["whoami"],
    "pwd": ["pwd"],
    "ls": ["ls", "-la", BASE_DIR],
    "df": ["df", "-h"],
    "free": ["free", "-h"],   # not present on macOS; system_monitor falls back gracefully
    "uptime": ["uptime"],
    "ps": ["ps", "-e"],
    "ps_aux": ["ps", "aux"],
    "wc_processes": ["ps", "aux"],  # piped through wc in system_monitor
}
