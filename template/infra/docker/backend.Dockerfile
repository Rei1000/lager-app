FROM python:3.11-slim

WORKDIR /app

COPY backend /app/backend

RUN if [ -f /app/backend/requirements.txt ]; then pip install -r /app/backend/requirements.txt; fi

CMD ["python", "-m", "http.server", "8000"]
