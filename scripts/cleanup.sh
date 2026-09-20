#!/usr/bin/env bash
# Removes __pycache__ directories and report files older than 7 days.
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null || true

if [ -d "reports" ]; then
  echo "Removing report files older than 7 days..."
  find reports -type f -mtime +7 -exec rm -f {} + 2>/dev/null || true
fi

echo "Cleanup complete."
