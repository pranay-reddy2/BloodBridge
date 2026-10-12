#!/bin/sh
# Apply database migrations, then hand PID 1 over to the API server so it receives
# SIGTERM directly from Kubernetes/Docker and shuts down gracefully.
set -eu

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "Running database migrations..."
  alembic upgrade head
fi

exec "$@"
