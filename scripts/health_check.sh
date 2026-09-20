#!/usr/bin/env bash
# Checks whether the Flask server is responding on port 5000.
set -e

URL="http://localhost:5000/dashboard"

if command -v curl >/dev/null 2>&1; then
  STATUS_CODE="$(curl -s -o /dev/null -w "%{http_code}" "$URL" || echo "000")"
else
  echo "curl not found — cannot perform HTTP health check."
  exit 1
fi

if [ "$STATUS_CODE" = "200" ]; then
  echo "Healthy: $URL responded with HTTP $STATUS_CODE."
  exit 0
else
  echo "Unhealthy: $URL responded with HTTP $STATUS_CODE (expected 200)."
  exit 1
fi
