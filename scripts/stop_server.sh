#!/usr/bin/env bash
# Stops the server started by start_server.sh.
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if [ ! -f "reports/server.pid" ]; then
  echo "No PID file found — is the server running?"
  exit 1
fi

PID="$(cat reports/server.pid)"
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  echo "Stopped server (PID $PID)."
else
  echo "Process $PID is not running."
fi

rm -f reports/server.pid
