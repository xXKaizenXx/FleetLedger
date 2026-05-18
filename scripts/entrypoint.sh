#!/bin/sh
set -e

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL must be set (PostgreSQL). Refusing to start."
  exit 1
fi

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"

python manage.py migrate --noinput
# Idempotent — repairs missing demo rows (vehicles, transactions) on every deploy.
python manage.py seed_demo

exec "$@"
