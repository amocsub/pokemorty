FROM python:3.10.13 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
RUN python -m venv .venv
COPY requirements.txt ./
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.10.13-slim
WORKDIR /app

COPY --from=builder /app/.venv .venv/
COPY . .

RUN mkdir -p /data

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_PATH=/data/hub.db

CMD ["/app/.venv/bin/gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]
