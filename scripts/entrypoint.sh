#!/bin/sh
set -e

python manage.py migrate --noinput
# Idempotent — repairs missing demo rows (vehicles, transactions) on every deploy.
python manage.py seed_demo

exec "$@"
