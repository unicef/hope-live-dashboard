#!/bin/bash
set -e
export MEDIA_ROOT="${MEDIA_ROOT:-/var/media}"
export STATIC_ROOT="${STATIC_ROOT:-/var/static}"

export REDIS_LOGLEVEL="${REDIS_LOGLEVEL:-warning}"
export REDIS_MAXMEMORY="${REDIS_MAXMEMORY:-100Mb}"
export REDIS_MAXMEMORY_POLICY="${REDIS_MAXMEMORY_POLICY:-volatile-ttl}"

export DOLLAR='$'

mkdir -p /var/run ${MEDIA_ROOT} ${STATIC_ROOT}
chown -R hope:unicef /var/run ${MEDIA_ROOT} ${STATIC_ROOT}
echo "created support dirs /var/run '${MEDIA_ROOT}' '${STATIC_ROOT}' "
echo "Startup command is: '$1'"

case "$1" in
    "run")
        django-admin upgrade

        exec uwsgi --ini /conf/uwsgi.ini

    ;;
    "dev")
        django-admin collectstatic --no-input
        django-admin migrate
        django-admin runserver 0.0.0.0:8000
    ;;
    "setup")
        django-admin upgrade
    ;;
    "worker")
        exec tini -- gosu hope:unicef celery -A hope_live.config worker --concurrency=4 -E -l "${CELERY_LOGLEVEL:-INFO}"
    ;;
    "beat")
        exec tini -- gosu hope:unicef celery -A hope_live.config beat --scheduler django_celery_beat.schedulers:DatabaseScheduler -l "${CELERY_LOGLEVEL:-INFO}"
    ;;
    "flower")
        exec tini -- gosu hope:unicef celery -A hope_live.config flower
    ;;
*)
exec "$@"
;;
esac
