# ---- Base image ----
    FROM python:3.11-slim

    # Fast, clean Python
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PIP_NO_CACHE_DIR=1
    
    # ---- OS deps (psycopg build, crypto, etc.) ----
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libssl-dev \
        pkg-config \
     && rm -rf /var/lib/apt/lists/*
    
    # ---- Workdir ----
    WORKDIR /app
    
    # ---- Python deps first (better layer caching) ----
    COPY requirements.txt /app/requirements.txt
    RUN python -m pip install --upgrade pip setuptools wheel \
     && pip install --no-cache-dir -r /app/requirements.txt
    
    # ---- App source ----
    COPY . /app
    
    # ---- Non-root user & writable dirs for signing keys ----
    # Use a fixed UID so mounted volumes don't get root-owned files.
    ARG APP_USER=appuser
    ARG APP_UID=10001
    RUN useradd -m -u ${APP_UID} ${APP_USER} \
     && mkdir -p /app/keys /app/tmp \
     && chown -R ${APP_USER}:${APP_USER} /app
    
    # If your code reads RESULTS_KEYS_DIR, set it here; else it uses /app/keys.
    ENV RESULTS_KEYS_DIR=/app/keys
    
    USER ${APP_USER}
    
    # Expose the service port (compose still maps it)
    EXPOSE 8004
    
    # ---- Default command (compose can override) ----
    CMD ["uvicorn", "services.results.app:app", "--host", "0.0.0.0", "--port", "8004"]
