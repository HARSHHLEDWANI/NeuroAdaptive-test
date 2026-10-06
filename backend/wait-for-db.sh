#!/bin/sh
set -eu
# Compose's one-shot migrate service owns schema changes and must succeed
# before the API/worker start. Native development runs alembic explicitly.
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log --reload \
  --reload-exclude 'var/uploads/*' --reload-exclude '**/__pycache__/*'
