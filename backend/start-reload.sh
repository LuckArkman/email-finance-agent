#!/usr/bin/env bash
set -e

# Start Uvicorn with live reload for development
# Change directory to src since our app is there, or run uvicorn passing the correct import path
cd src

echo "Starting Uvicorn Server with live reload..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
