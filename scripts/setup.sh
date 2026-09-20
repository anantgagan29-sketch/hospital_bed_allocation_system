#!/usr/bin/env bash
# Prepares the environment: virtualenv, dependencies, database.
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "== Hospital Bed Allocation Platform: setup =="

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

echo "Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "Initializing database..."
python3 database/init_db.py

mkdir -p reports

chmod +x scripts/*.sh

echo "Setup complete. Run ./scripts/start_server.sh to start the app."
