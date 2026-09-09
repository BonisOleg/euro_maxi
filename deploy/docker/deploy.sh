#!/usr/bin/env bash
# HTTP-first деплой на Droplet (django-droplet-http-first).
# SSL не вмикати тут. Після зміни .env — цей скрипт (force-recreate), не лише up -d.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.prod.yml)

if [ ! -f .env ]; then
  echo "[deploy] Немає .env — скопіюй .env.docker.example і заповни SECRET_KEY / POSTGRES_PASSWORD" >&2
  exit 1
fi

if grep -E '^ALLOWED_HOSTS=.*DROPLET_IP' .env; then
  echo "[deploy] ALLOWED_HOSTS містить літерал DROPLET_IP — постав IPv4, інакше 400 на сайт (ERR-10)" >&2
  exit 1
fi

if grep -Eq '^SECURE_SSL=\s*(True|true|1)\s*$' .env; then
  echo "[deploy] SECURE_SSL=True на HTTP-first зламає кошик/адмінку. Постав False до SSL." >&2
  exit 1
fi

HOST_IP="$(grep -E '^ALLOWED_HOSTS=' .env | head -1 | cut -d= -f2- | cut -d, -f1 | tr -d '[:space:]')"
if [ -z "$HOST_IP" ] || [ "$HOST_IP" = "DROPLET_IP" ]; then
  echo "[deploy] ALLOWED_HOSTS має починатись з реального IPv4" >&2
  exit 1
fi

free_host_ports() {
  systemctl stop nginx 2>/dev/null || true
  systemctl disable nginx 2>/dev/null || true
  systemctl stop gunicorn 2>/dev/null || true
}

if [ "$(id -u)" -eq 0 ]; then
  free_host_ports
fi

echo "[deploy] build + up --force-recreate (env перечитується лише так)"
"${COMPOSE[@]}" build
"${COMPOSE[@]}" up -d --force-recreate --remove-orphans

echo "[deploy] очікую /healthz/ ..."
ok=0
for _ in $(seq 1 40); do
  if curl -sf "http://127.0.0.1/healthz/" >/dev/null; then
    ok=1
    break
  fi
  sleep 3
done
if [ "$ok" -ne 1 ]; then
  echo "[deploy] healthz не піднявся. Логи web:" >&2
  "${COMPOSE[@]}" logs --tail=80 web >&2
  exit 1
fi

echo "[deploy] перевірка Host=$HOST_IP на /healthz/ (не чіпати / до loaddata)"
code="$(curl -s -o /dev/null -w '%{http_code}' -H "Host: ${HOST_IP}" "http://127.0.0.1/healthz/")"
echo "[deploy] GET /healthz/ Host=$HOST_IP → HTTP $code"
if [ "$code" = "400" ]; then
  echo "[deploy] DisallowedHost: ALLOWED_HOSTS не містить $HOST_IP (ERR-10)" >&2
  exit 1
fi
if [ "$code" != "200" ]; then
  echo "[deploy] неочікуваний код $code" >&2
  exit 1
fi

echo "[deploy] сервіси:"
"${COMPOSE[@]}" ps
for svc in db web nginx; do
  if ! "${COMPOSE[@]}" ps --status running --services 2>/dev/null | grep -qx "$svc"; then
    echo "[deploy] увага: $svc не в --status running (Compose інколи друкує Up — дивись healthz)"
  fi
done

echo "[deploy] HTTP-first OK. Далі: sync-data.sh import (якщо є dump) → createsuperuser"
echo "[deploy] curl -sI -H \"Host: ${HOST_IP}\" http://127.0.0.1/ | head -5"
