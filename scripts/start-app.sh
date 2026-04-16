#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
FRONTEND_ENV_FILE="$FRONTEND_DIR/.env.local"
RUN_DIR="$ROOT_DIR/.run"
LOG_DIR="$ROOT_DIR/.run/logs"

MODE="${1:-}"
[[ -n "${1:-}" ]] && shift || true

REBUILD=0
WITH_TESTSERVER="${WITH_TESTSERVER:-0}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --rebuild|--build)
      REBUILD=1
      ;;
    --with-testserver|-t)
      WITH_TESTSERVER=1
      ;;
    *)
      printf '[start-app] FEHLER: Unbekanntes Argument: %s (erlaubt: --rebuild, --build, --with-testserver, -t)\n' "$1" >&2
      exit 1
      ;;
  esac
  shift
done

usage() {
  cat <<'EOF'
Verwendung:
  ./scripts/start-app.sh localhost [OPTIONEN]
  ./scripts/start-app.sh lan [OPTIONEN]
  ./scripts/start-app.sh tailscale [OPTIONEN]

Modi:
  localhost  Start fuer lokale Nutzung nur auf dem Mac (localhost)
  lan        Start fuer Nutzung im Heimnetz (LAN-IP des Macs)
  tailscale  Ermittelt automatisch die Tailscale-IP und setzt Frontend-ENV auf diese IP

Optionen (beliebige Reihenfolge):
  (keine)       Schneller Neustart: docker compose up ohne --build (kein Image-Rebuild)
  --rebuild     Backend-Image neu bauen (pip install im Dockerfile), wie frueher bei jedem Start
  --build       Alias fuer --rebuild
  --with-testserver, -t
                Startet zusaetzlich python3 -m http.server 9999
  WITH_TESTSERVER=1  Alternative zum Testserver-Flag

Beispiele:
  ./scripts/start-app.sh localhost
  ./scripts/start-app.sh localhost --rebuild
  ./scripts/start-app.sh lan --with-testserver
EOF
}

log() {
  printf '[start-app] %s\n' "$1"
}

abort() {
  printf '[start-app] FEHLER: %s\n' "$1" >&2
  exit 1
}

kill_port() {
  local port="$1"
  local pids
  pids="$(lsof -ti "tcp:${port}" || true)"
  if [[ -z "$pids" ]]; then
    log "Port ${port} ist frei"
    return
  fi

  log "Beende Prozesse auf Port ${port}: $pids"
  # shellcheck disable=SC2086
  kill $pids || true
  sleep 1
  pids="$(lsof -ti "tcp:${port}" || true)"
  if [[ -n "$pids" ]]; then
    log "Erzwinge Beenden auf Port ${port}: $pids"
    # shellcheck disable=SC2086
    kill -9 $pids || true
  fi
}

wait_for_http() {
  local url="$1"
  local timeout_seconds="${2:-40}"
  local start_ts
  start_ts="$(date +%s)"
  while true; do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    if (( "$(date +%s)" - start_ts >= timeout_seconds )); then
      return 1
    fi
    sleep 1
  done
}

is_private_ipv4() {
  local ip="$1"
  [[ "$ip" =~ ^10\. ]] && return 0
  [[ "$ip" =~ ^192\.168\. ]] && return 0
  if [[ "$ip" =~ ^172\.([1][6-9]|2[0-9]|3[0-1])\. ]]; then
    return 0
  fi
  return 1
}

resolve_lan_ip() {
  local iface ip

  iface="$(route -n get default 2>/dev/null | awk '/interface:/{print $2; exit}')"
  if [[ -n "${iface:-}" ]]; then
    ip="$(ipconfig getifaddr "$iface" 2>/dev/null || true)"
    if [[ -n "$ip" ]] && is_private_ipv4 "$ip"; then
      echo "$ip"
      return 0
    fi
  fi

  ip="$(
    ifconfig 2>/dev/null | awk '
      /^[a-z0-9]/ { iface=$1; sub(":", "", iface) }
      /inet / {
        candidate=$2
        if (candidate ~ /^127\./) next
        if (iface ~ /^utun/ || iface ~ /^lo/ || iface ~ /^docker/ || iface ~ /^bridge/ || iface ~ /^veth/) next
        if (candidate ~ /^192\.168\./ || candidate ~ /^10\./ || candidate ~ /^172\.(1[6-9]|2[0-9]|3[0-1])\./) {
          print candidate
          exit
        }
      }
    '
  )"
  if [[ -n "$ip" ]]; then
    echo "$ip"
    return 0
  fi

  return 1
}

[[ -n "$MODE" ]] || {
  usage
  exit 1
}

if [[ "$MODE" == "local" ]]; then
  MODE="localhost"
fi

if [[ "$MODE" != "localhost" && "$MODE" != "lan" && "$MODE" != "tailscale" ]]; then
  usage
  exit 1
fi

mkdir -p "$RUN_DIR" "$LOG_DIR"

log "Modus: $MODE"
kill_port 3001
kill_port 9999

TAILSCALE_IP=""
LAN_IP=""
FRONTEND_PUBLIC_URL=""
BACKEND_URL=""
API_BASE_URL=""
MOBILE_APP_URL=""
FRONTEND_ORIGIN=""
CORS_ALLOW_ORIGINS=""

write_frontend_env_file() {
  cat >"$FRONTEND_ENV_FILE" <<EOF
# AUTO-GENERIERT durch scripts/start-app.sh
# Modus: $MODE
NEXT_PUBLIC_API_BASE_URL=$API_BASE_URL
NEXT_PUBLIC_MOBILE_APP_URL=$MOBILE_APP_URL
EOF
}

if [[ "$MODE" == "localhost" ]]; then
  API_BASE_URL="http://localhost:8001"
  MOBILE_APP_URL="http://localhost:3001/login"
  FRONTEND_ORIGIN="http://localhost:3001"
  FRONTEND_PUBLIC_URL="$MOBILE_APP_URL"
  BACKEND_URL="$API_BASE_URL"
elif [[ "$MODE" == "lan" ]]; then
  LAN_IP="$(resolve_lan_ip || true)"
  [[ -n "$LAN_IP" ]] || abort "keine gueltige LAN-IP gefunden"
  API_BASE_URL="http://${LAN_IP}:8001"
  MOBILE_APP_URL="http://${LAN_IP}:3001/login"
  FRONTEND_ORIGIN="http://${LAN_IP}:3001"
  FRONTEND_PUBLIC_URL="$MOBILE_APP_URL"
  BACKEND_URL="$API_BASE_URL"
elif [[ "$MODE" == "tailscale" ]]; then
  command -v tailscale >/dev/null 2>&1 || abort "tailscale CLI nicht gefunden"
  TAILSCALE_IP="$(tailscale ip -4 | awk 'NF {print; exit}')"
  [[ -n "$TAILSCALE_IP" ]] || abort "keine Tailscale IPv4 gefunden"
  API_BASE_URL="http://${TAILSCALE_IP}:8001"
  MOBILE_APP_URL="http://${TAILSCALE_IP}:3001/login"
  FRONTEND_ORIGIN="http://${TAILSCALE_IP}:3001"
  FRONTEND_PUBLIC_URL="$MOBILE_APP_URL"
  BACKEND_URL="$API_BASE_URL"
fi

CORS_ALLOW_ORIGINS="http://localhost:3001"
if [[ "$FRONTEND_ORIGIN" != "http://localhost:3001" ]]; then
  CORS_ALLOW_ORIGINS="${CORS_ALLOW_ORIGINS},${FRONTEND_ORIGIN}"
fi

cd "$ROOT_DIR"
CORS_ALLOW_ORIGINS="$CORS_ALLOW_ORIGINS" docker compose down
if [[ "$REBUILD" == "1" ]]; then
  log "Docker: compose up -d --build (Backend-Image wird neu gebaut, inkl. pip install im Dockerfile)"
  CORS_ALLOW_ORIGINS="$CORS_ALLOW_ORIGINS" docker compose up -d --build
else
  log "Docker: compose up -d ohne --build (bestehendes Backend-Image, schneller Neustart)"
  CORS_ALLOW_ORIGINS="$CORS_ALLOW_ORIGINS" docker compose up -d
fi

log "Frontend Build-Cache (.next) wird geloescht"
rm -rf "$FRONTEND_DIR/.next"

log "Schreibe Frontend ENV nach $FRONTEND_ENV_FILE"
write_frontend_env_file

FRONTEND_LOG="$LOG_DIR/frontend-dev.log"
FRONTEND_PID_FILE="$RUN_DIR/frontend-dev.pid"

log "Starte Frontend Dev-Server im Hintergrund"
(
  cd "$FRONTEND_DIR"
  NEXT_PUBLIC_API_BASE_URL="$API_BASE_URL" \
  NEXT_PUBLIC_MOBILE_APP_URL="$MOBILE_APP_URL" \
  HOST=0.0.0.0 \
  nohup npm run dev >"$FRONTEND_LOG" 2>&1 &
  echo $! >"$FRONTEND_PID_FILE"
)

TESTSERVER_URL=""
TESTSERVER_LOG="$LOG_DIR/python-testserver.log"
TESTSERVER_PID_FILE="$RUN_DIR/python-testserver.pid"

if [[ "$WITH_TESTSERVER" == "1" ]]; then
  log "Starte optionalen Python-Testserver auf Port 9999"
  (
    cd "$ROOT_DIR"
    nohup python3 -m http.server 9999 >"$TESTSERVER_LOG" 2>&1 &
    echo $! >"$TESTSERVER_PID_FILE"
  )
  TESTSERVER_URL="http://localhost:9999"
fi

if wait_for_http "http://localhost:8001/health" 60; then
  BACKEND_STATUS="OK"
else
  BACKEND_STATUS="NICHT ERREICHBAR"
fi

if wait_for_http "http://localhost:3001/login" 60; then
  FRONTEND_STATUS="OK"
else
  FRONTEND_STATUS="NICHT ERREICHBAR"
fi

echo
echo "===== Lager-App Starter ====="
echo "Modus:                 $MODE"
if [[ -n "$TAILSCALE_IP" ]]; then
  echo "Verwendete IP:         $TAILSCALE_IP"
elif [[ -n "$LAN_IP" ]]; then
  echo "Verwendete IP:         $LAN_IP"
else
  echo "Verwendete IP:         localhost"
fi
echo "Frontend URL:          $FRONTEND_PUBLIC_URL"
echo "Backend URL:           $BACKEND_URL"
echo "API BASE URL (ENV):    $API_BASE_URL"
echo "MOBILE URL (ENV):      $MOBILE_APP_URL"
if [[ -n "$TESTSERVER_URL" ]]; then
  echo "Python-Testserver URL: $TESTSERVER_URL"
else
  echo "Python-Testserver URL: nicht gestartet"
fi
echo "Frontend Status:       $FRONTEND_STATUS"
echo "Backend Status:        $BACKEND_STATUS"
echo "Frontend Log:          $FRONTEND_LOG"
if [[ -n "$TESTSERVER_URL" ]]; then
  echo "Testserver Log:        $TESTSERVER_LOG"
fi
echo "============================="
