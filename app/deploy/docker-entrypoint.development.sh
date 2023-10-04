#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

rm -rf /static/*

# echo "Start with a fresh database"
# export PGPASSWORD=${DATABASE_PASSWORD}
# psql -h ${DATABASE_HOST_OVERRIDE} -p 5432 -d ${DATABASE_NAME} -U ${DATABASE_USER} -c "drop schema public cascade;"
# psql -h ${DATABASE_HOST_OVERRIDE} -p 5432 -d ${DATABASE_NAME} -U ${DATABASE_USER} -c "create schema public;"

echo Apply migrations
python manage.py migrate --noinput

echo Create superuser
python manage.py createsuperuser --noinput || true

exec python -m debugpy --listen 0.0.0.0:5678 /app/manage.py runserver 0.0.0.0:8000
