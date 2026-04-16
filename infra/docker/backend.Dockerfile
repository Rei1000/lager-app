FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend/src

WORKDIR /app

# Nur Dependency-Definition zuerst — Layer bleibt gecacht, solange pyproject.toml unverändert ist.
COPY backend/pyproject.toml /app/backend/pyproject.toml
WORKDIR /app/backend
RUN python - <<'PY'
import subprocess
import sys
import tomllib

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)
project = data["project"]
deps = list(project["dependencies"])
opt = project.get("optional-dependencies") or {}
deps += list(opt.get("dev", []))
subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", *deps])
PY

# Anwendungscode (häufige Änderungen) — löst kein erneutes pip install aus, solange pyproject gleich bleibt.
WORKDIR /app
COPY backend /app/backend
COPY infra/docker/backend-entrypoint.sh /app/infra/docker/backend-entrypoint.sh
RUN chmod +x /app/infra/docker/backend-entrypoint.sh

CMD ["/app/infra/docker/backend-entrypoint.sh"]
