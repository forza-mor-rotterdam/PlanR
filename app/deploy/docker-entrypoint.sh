#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

# echo "Start with a fresh database"
# export PGPASSWORD=${DATABASE_PASSWORD}
# psql -h ${DATABASE_HOST_OVERRIDE} -p 5432 -d ${DATABASE_NAME} -U ${DATABASE_USER} -c "drop schema public cascade;"
# psql -h ${DATABASE_HOST_OVERRIDE} -p 5432 -d ${DATABASE_NAME} -U ${DATABASE_USER} -c "create schema public;"

UWSGI_LOG="/app/uwsgi.log"
touch "$UWSGI_LOG"
chown $APP_USER:$APP_USER "$UWSGI_LOG"
chmod 744 "$UWSGI_LOG"

UWSGI_LOG="/uwsgi.log"
touch "$UWSGI_LOG"
chown $APP_USER:$APP_USER "$UWSGI_LOG"
chmod 744 "$UWSGI_LOG"

UWSGI_LOG="uwsgi.log"
touch "$UWSGI_LOG"
chown $APP_USER:$APP_USER "$UWSGI_LOG"
chmod 744 "$UWSGI_LOG"

echo Apply migrations
python manage.py migrate --noinput

echo Collecting static files
python manage.py collectstatic --no-input

echo Create superuser
python manage.py createsuperuser --noinput || true

exec uwsgi --ini /app/deploy/config.ini
