#!/usr/bin/env bash
# Перенос локальної SQLite-вітрини (каталог + CMS + media) у Postgres на Droplet.
# Порядок: healthz OK → import → createsuperuser (ніколи суперюзер до flush/loaddata).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
DATA_DIR="$ROOT/deploy/data"
FIXTURE="$DATA_DIR/storefront.json"
MEDIA_TAR="$DATA_DIR/media.tar.gz"

COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.prod.yml)

usage() {
  cat <<'EOF'
Usage:
  ./deploy/docker/sync-data.sh export
  ./deploy/docker/sync-data.sh push user@host:/var/www/euromaxi --yes
  ./deploy/docker/sync-data.sh import [--flush]
EOF
  exit 1
}

cmd="${1:-}"
shift || true

export_data() {
  mkdir -p "$DATA_DIR"
  echo "[sync] dumpdata catalog + content (без звернень)"
  ./venv/bin/python3 manage.py dumpdata catalog content \
    --exclude content.ContactMessage \
    --indent 2 -o "$FIXTURE"
  echo "[sync] tar media/"
  tar -czf "$MEDIA_TAR" -C "$ROOT" media
  ls -lh "$FIXTURE" "$MEDIA_TAR"
}

push_data() {
  target="${1:-}"
  yes_flag="${2:-}"
  if [ -z "$target" ]; then
    echo "[sync] вкажи user@host:/var/www/euromaxi" >&2
    exit 1
  fi
  if [ ! -f "$FIXTURE" ] || [ ! -f "$MEDIA_TAR" ]; then
    echo "[sync] спочатку: $0 export" >&2
    exit 1
  fi
  if [ "$yes_flag" != "--yes" ]; then
    echo "[sync] буде scp на $target/deploy/data/  (додай --yes)" >&2
    exit 1
  fi
  host="${target%%:*}"
  dest="${target#*:}"
  ssh "$host" "mkdir -p ${dest}/deploy/data"
  scp "$FIXTURE" "$MEDIA_TAR" "${target}/deploy/data/"
  echo "[sync] на сервері: cd ${dest} && bash deploy/docker/sync-data.sh import"
}

import_data() {
  flush="${1:-}"
  if [ ! -f "$FIXTURE" ]; then
    echo "[sync] немає $FIXTURE" >&2
    exit 1
  fi
  if [ "$flush" = "--flush" ]; then
    echo "[sync] flush (стирає auth.User — createsuperuser ПІСЛЯ цього)"
    "${COMPOSE[@]}" exec -T web python3 manage.py flush --noinput
  fi
  echo "[sync] loaddata"
  "${COMPOSE[@]}" cp "$FIXTURE" web:/tmp/storefront.json
  "${COMPOSE[@]}" exec -T web python3 manage.py loaddata /tmp/storefront.json
  if [ -f "$MEDIA_TAR" ]; then
    echo "[sync] media → /app/media (volume)"
    "${COMPOSE[@]}" cp "$MEDIA_TAR" web:/tmp/media.tar.gz
    "${COMPOSE[@]}" exec -T web tar -xzf /tmp/media.tar.gz -C /app
  fi
  echo "[sync] import OK. Далі createsuperuser:"
  echo "  docker compose -f docker-compose.yml -f docker-compose.prod.yml exec web python3 manage.py createsuperuser"
}

case "$cmd" in
  export) export_data ;;
  push) push_data "${1:-}" "${2:-}" ;;
  import) import_data "${1:-}" ;;
  *) usage ;;
esac
