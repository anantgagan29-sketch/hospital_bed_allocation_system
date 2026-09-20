#!/usr/bin/env bash
# Starts the Flask development server in the background and records its PID.
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
mkdir -p reports

if [ -f "venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

if [ -f "reports/server.pid" ] && kill -0 "$(cat reports/server.pid)" 2>/dev/null; then
  echo "Server already running with PID $(cat reports/server.pid)."
  exit 0
fi

echo "Starting Flask server on http://localhost:5000 ..."
nohup python3 app.py > reports/server.log 2>&1 &
echo $! > reports/server.pid
echo "Server started with PID $(cat reports/server.pid). Logs: reports/server.log"
