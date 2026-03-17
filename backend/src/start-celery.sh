#!/usr/bin/env bash
set -e

# Wait a bit for Redis to become available (simple sleep for dev purposes)
echo "Starting Celery Worker..."

cd /app/src || cd .
celery -A app.celery_app:celery_app worker -Q ai_queue,celery --loglevel=info --concurrency=2
