#!/usr/bin/env bash

set -euo pipefail

uv run alembic upgrade head

api_pid=""
consumer_pid=""

stop_children() {
    trap - TERM INT
    kill "$api_pid" "$consumer_pid" 2>/dev/null || true
    wait 2>/dev/null || true
}

on_signal() {
    stop_children
    exit 0
}
trap on_signal TERM INT

uv run uvicorn bin.api:app --host 0.0.0.0 --port 8000 &
api_pid=$!

uv run python -m bin.consumer &
consumer_pid=$!

set +e
wait -n
status=$?
set -e

echo "start.sh: a child process exited with status ${status}, stopping container"
stop_children
exit "${status}"
