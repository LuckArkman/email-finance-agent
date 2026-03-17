#!/usr/bin/env bash
set -e

# Change directory to where app module is
cd src

echo "Applying database migrations (Placeholder for Alembic)..."
# alembic upgrade head

echo "Starting Uvicorn Server in PRODUCTION mode..."
# Use multiple workers for production
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
