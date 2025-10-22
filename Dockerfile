# ---- Base image ----
    FROM python:3.11-slim

    # Ensure Python prints straight to logs and no .pyc files
    ENV PYTHONUNBUFFERED=1 \
        PYTHONDONTWRITEBYTECODE=1 \
        PIP_NO_CACHE_DIR=1
    
    # ---- OS deps (build + pg + crypto) ----
    # libpq-dev for psycopg, build-essential for any wheels that need compile,
    # libssl-dev/pkg-config help some crypto libs
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libssl-dev \
        pkg-config \
        && rm -rf /var/lib/apt/lists/*
    
    # ---- Workdir ----
    WORKDIR /app
    
    # ---- Python deps first (better layer caching) ----
    COPY requirements.txt .
    RUN python -m pip install --upgrade pip setuptools wheel \
     && pip install --no-cache-dir -r requirements.txt
    
    # ---- App source ----
    COPY . .
    
    # ---- (Optional) run as non-root ----
    # Create an unprivileged user and switch to it
    RUN useradd -m appuser
    USER appuser
    
    # ---- Default command (compose will override per service) ----
    # Keep a harmless default; compose sets the real uvicorn target
    CMD ["python", "-c", "print('Specify a command in docker-compose')"]