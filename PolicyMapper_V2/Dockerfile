# Dockerfile
FROM python:3.11-slim

# 1) Install system libraries that WeasyPrint (and ffmpeg) need:
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      git \
      curl \
      ffmpeg \
      libcairo2 \
      libpango-1.0-0 \
      libpangocairo-1.0-0 \
      libgdk-pixbuf2.0-0 \
      libffi-dev \
      shared-mime-info \
      && rm -rf /var/lib/apt/lists/*

# 2) Set a working directory
WORKDIR /app

# 3) Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Install Whisper (if you need it)
RUN pip install --no-cache-dir git+https://github.com/openai/whisper.git

# 5) Copy your app code
COPY . .

# 6) Expose port & define entrypoint
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]