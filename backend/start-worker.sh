#!/bin/sh
set -eu
exec celery -A app.core.celery_app.celery_app worker --loglevel=INFO --concurrency="${WORKER_CONCURRENCY_V1:-2}"
