FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code and the results service
COPY common /app/common
COPY services/results /app/services/results

EXPOSE 8004
CMD ["uvicorn", "services.results.app:app", "--host", "0.0.0.0", "--port", "8004"]
