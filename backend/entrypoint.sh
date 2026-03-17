#!/usr/bin/env bash
set -e

# This is a placeholder for wait-for-it script logic.
# You can use it to block the startup until a dependency (like PostgreSQL or Redis) is fully available.
# Example:
# while ! nc -z db 5432; do   
#   echo "Waiting for PostgreSQL to start..."
#   sleep 1
# done

echo "Dependencies ready. Starting backend service..."

# Evaluate the passed command
exec "$@"
