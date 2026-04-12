FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend/src

WORKDIR /app

COPY backend /app/backend
COPY infra/docker/backend-entrypoint.sh /app/infra/docker/backend-entrypoint.sh

RUN pip install --no-cache-dir "/app/backend[dev]"
RUN chmod +x /app/infra/docker/backend-entrypoint.sh

CMD ["/app/infra/docker/backend-entrypoint.sh"]
