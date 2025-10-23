FROM python:3.11-slim

# 1) System deps for building common Python wheels (crypto, postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Upgrade pip toolchain before installing requirements
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# 3) Copy source code last (keeps caches if only code changes)
COPY . .

# Overridden by docker-compose; left here as a default
CMD ["python", "-c", "print('Specify a command in docker-compose')"]
