#!/bin/sh
set -eu

echo "Starte Backend-Bootstrap..."
cd /app/backend

attempt=1
max_attempts="${BOOTSTRAP_MAX_ATTEMPTS:-25}"
while [ "$attempt" -le "$max_attempts" ]; do
  if alembic upgrade head; then
    break
  fi
  echo "Migration fehlgeschlagen (Versuch $attempt/$max_attempts), warte auf DB..."
  attempt=$((attempt + 1))
  sleep 2
done

if [ "$attempt" -gt "$max_attempts" ]; then
  echo "Migration konnte nicht ausgefuehrt werden. Abbruch."
  exit 1
fi

if [ "${DEMO_SEED_ON_STARTUP:-true}" = "true" ]; then
  echo "Fuehre Demo-Seed aus (idempotent)..."
  python -m scripts.seed_demo_data
fi

mkdir -p "${PHOTO_UPLOAD_DIRECTORY:-uploads}"

echo "Starte API..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
