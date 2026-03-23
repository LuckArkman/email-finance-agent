# Stage 1: Builder
FROM python:3.12-slim as builder

# Networking and Poetry Config
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_REQUESTS_TIMEOUT=1200 \
    POETRY_HTTP_TIMEOUT=1200 \
    PIP_DEFAULT_TIMEOUT=1200

ENV PATH="$POETRY_HOME/bin:$PATH"

# Install System dependencies and Poetry
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY src/pyproject.toml src/poetry.lock* ./

# Install project dependencies
# Note: LayoutLMv3, Transformers and Pytorch pull massive nvidia/cudnn binaries (~4GB+)
# This requires a very stable connection or multiple retries.
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
COPY entrypoint.sh start-reload.sh start.sh ./
RUN chmod +x /app/entrypoint.sh /app/start-reload.sh /app/start.sh

# Copy application source
COPY src/ ./src/

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/app/start-reload.sh"]
