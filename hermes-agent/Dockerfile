FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including Node.js and npm
RUN apt-get update -qq && \
    apt-get install -y -qq curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y -qq nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --quiet --no-cache-dir hermes-agent httpx

# The configuration and skills will be mounted as a volume.
# For runtime, we just copy the initial config to the expected path and run the gateway.
CMD cp /app/config.yaml /root/.hermes/config.yaml && \
    cp -r /app/skills /root/.hermes/skills && \
    cp -r /app/hooks /root/.hermes/hooks && \
    hermes gateway
