#!/usr/bin/env bash
# Collects OS/kernel/CPU/memory/disk/process/uptime info into a report file.
# Uses Linux commands where available and falls back gracefully elsewhere
# (this repo is developed cross-platform but meant to be run on Linux).
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
mkdir -p reports

REPORT="reports/system_report.txt"

{
  echo "Hospital Bed Allocation Platform — System Report"
  echo "Generated: $(date)"
  echo "================================================"

  echo -e "\n--- OS / Kernel Information (uname -a) ---"
  uname -a

  echo -e "\n--- Current User (whoami) ---"
  whoami

  echo -e "\n--- Working Directory (pwd) ---"
  pwd

  echo -e "\n--- CPU Information ---"
  if command -v lscpu >/dev/null 2>&1; then
    lscpu
  elif [ -f /proc/cpuinfo ]; then
    grep -m1 "model name" /proc/cpuinfo
  else
    sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "CPU info command not available on this OS."
  fi

  echo -e "\n--- Memory Usage ---"
  if command -v free >/dev/null 2>&1; then
    free -h
  else
    echo "free -h not available on this OS (Linux-only). vm_stat sample:"
    vm_stat 2>/dev/null || echo "No memory command available."
  fi

  echo -e "\n--- Disk Usage (df -h) ---"
  df -h

  echo -e "\n--- Running Process Count (ps aux | wc -l) ---"
  ps aux | wc -l

  echo -e "\n--- System Uptime ---"
  uptime

} > "$REPORT"

echo "System report written to $REPORT"
cat "$REPORT"
