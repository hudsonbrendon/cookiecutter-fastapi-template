FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# First copy only requirements.txt to cache dependencies independently
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


COPY . /app

EXPOSE 80

ENV UVICORN_HOST=0.0.0.0 UVICORN_PORT=80 UVICORN_LOG_LEVEL=info
