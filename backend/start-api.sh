#!/bin/sh
set -eu
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --no-access-log --workers "${API_WORKERS_V1:-1}"
