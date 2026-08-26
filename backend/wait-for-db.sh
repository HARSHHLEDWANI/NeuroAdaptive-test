#!/bin/sh

echo "Waiting for Postgres..."

while ! nc -z db 5432; do
  sleep 1
done

echo "Postgres started"

alembic upgrade head

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload