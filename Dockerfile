# Dockerfile (repo root)
FROM python:3.11-slim

# Optional system deps if you build wheels locally (cryptography, psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole source tree (common, services, cryptoutils, infra, etc.)
COPY . .

# Make top-level packages importable
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
