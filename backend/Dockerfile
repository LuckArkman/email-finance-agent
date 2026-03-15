# Stage 1: Builder
FROM python:3.12-slim as builder

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential \
    && curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Copy poetry configuration
COPY src/pyproject.toml src/poetry.lock* ./

# Install dependencies
RUN poetry install --no-root --without dev

# Stage 2: Runtime
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install runtime system dependencies (netcat for wait-for-it)
RUN apt-get update && apt-get install -y --no-install-recommends netcat-traditional && rm -rf /var/lib/apt/lists/*

# Copy virtual env from builder
COPY --from=builder /app/.venv /app/.venv

# Copy scripts and set permissions
COPY entrypoint.sh start-reload.sh ./
RUN chmod +x /app/entrypoint.sh /app/start-reload.sh

# Copy application source
COPY src/ ./src/

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/app/start-reload.sh"]
