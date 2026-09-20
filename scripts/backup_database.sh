#!/usr/bin/env bash
# Copies the SQLite database into reports/ with a timestamp in the filename.
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
mkdir -p reports

DB_PATH="database/hospital.db"
if [ ! -f "$DB_PATH" ]; then
  echo "No database found at $DB_PATH — run setup.sh first."
  exit 1
fi

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_PATH="reports/hospital_backup_${TIMESTAMP}.db"

cp "$DB_PATH" "$BACKUP_PATH"
echo "Database backed up to $BACKUP_PATH"
