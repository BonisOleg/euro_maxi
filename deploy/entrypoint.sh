#!/bin/sh
set -e

echo "[entrypoint] Очікування PostgreSQL..."
python3 - <<'PYEOF'
import os
import sys
import time

import psycopg2

for attempt in range(30):
    try:
        psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB", "euromaxi"),
            user=os.environ.get("POSTGRES_USER", "euromaxi"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
            host=os.environ.get("POSTGRES_HOST", "db"),
            port=os.environ.get("POSTGRES_PORT", "5432"),
        ).close()
        print("[entrypoint] PostgreSQL готовий.")
        sys.exit(0)
    except psycopg2.OperationalError:
        time.sleep(1)
print("[entrypoint] PostgreSQL не відповів за 30с.", file=sys.stderr)
sys.exit(1)
PYEOF

echo "[entrypoint] Застосування міграцій..."
python3 manage.py migrate --noinput

echo "[entrypoint] Збір статики..."
python3 manage.py collectstatic --noinput

echo "[entrypoint] Запуск gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
