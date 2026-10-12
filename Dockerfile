FROM python:3.10-slim

# ffmpeg is required by Whisper to decode audio files
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces containers run as a non-root user (uid 1000)
RUN useradd -m -u 1000 appuser
USER appuser
ENV HOME=/home/appuser \
    PATH=/home/appuser/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir --user --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --user --no-build-isolation -r requirements.txt

COPY --chown=appuser:appuser . .

# Cache dir for the Whisper model weights (must be writable by appuser)
ENV XDG_CACHE_HOME=$HOME/.cache

ENV PORT=7860
EXPOSE 7860

CMD ["python", "app.py"]
