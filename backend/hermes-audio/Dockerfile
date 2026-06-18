FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update -qq && \
    apt-get install -y -qq ffmpeg git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt .

# Install torch and torchaudio CPU only first (smaller image, no CUDA bloat)
RUN pip install --no-cache-dir torch==2.3.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and reference speaker audio
COPY main.py .
COPY reference_speaker.wav .

# Set Coqui TOS environment variable to avoid interactive prompts
ENV COQUI_TOS_AGREED=1

# Expose the API port
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
