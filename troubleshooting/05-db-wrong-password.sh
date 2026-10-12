#!/usr/bin/env bash
# SCENARIO 5 — the real application loses its database credentials.
# Breaks the live BloodBridge backend by pointing it at a Secret with a wrong password,
# so the new pods cannot run their migrations and crash-loop.
# Restore with:  ./troubleshooting/05-db-wrong-password.sh --restore
set -euo pipefail
NS=bloodbridge
DEPLOY=bloodbridge-backend

if [[ "${1:-}" == "--restore" ]]; then
  kubectl rollout undo deployment/$DEPLOY -n $NS
  echo "Restored. (If Argo CD self-heal is on it will also revert the change automatically.)"
  exit 0
fi

kubectl set env deployment/$DEPLOY -n $NS DB_PASSWORD=definitely-wrong
echo "Backend now uses a wrong DB password. Investigate with the RUNBOOK (scenario 5)."
