# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy original requirements.txt
COPY requirements.txt .

# 🧹 Remove only 'tensorflow-intel' (leave 'tensorflow' as is)
RUN grep -v "^tensorflow_intel" requirements.txt > filtered-requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --prefer-binary --timeout 300 --retries 10 --no-cache-dir -r filtered-requirements.txt

# Copy the whole project
COPY . .

# Expose FastAPI port
EXPOSE 8002

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
