#!/bin/sh -e

export UWSGI_PROCESSES="${UWSGI_PROCESSES:-"4"}"
export DJANGO_SETTINGS_MODULE="hope_live.config.settings"

mkdir -p /var/run ${MEDIA_ROOT} ${STATIC_ROOT}

if [ -d "${MEDIA_ROOT}" ];then
  chown -R hope:unicef ${MEDIA_ROOT}
fi

if [ -d "${STATIC_ROOT}" ];then
  chown -R hope:unicef ${STATIC_ROOT}
fi

mkdir -p /app/
chown -R hope:unicef /app
cd /app

case "$1" in
    run)
        django-admin upgrade --with-check
        MAPPING=""
        if [ "${STATIC_URL}" = "/static/" ]; then
            MAPPING="--static-map ${STATIC_URL}=${STATIC_ROOT}"
        fi
        exec tini -- uwsgi --http :8000 \
            -H /venv \
            --module hope_live.config.wsgi \
            --mimefile=/conf/mime.types \
            --uid hope \
            --gid unicef \
            --buffer-size 8192 \
            --http-buffer-size 8192 \
            $MAPPING
        ;;
    dev)
        until pg_isready -h db -p 5432; do
            echo "waiting for database"
            sleep 2
        done
        django-admin collectstatic --no-input
        django-admin migrate
        exec django-admin runserver 0.0.0.0:8000
        ;;
    upgrade)
        exec django-admin upgrade --with-check
        ;;
    worker)
        exec tini -- gosu hope:unicef celery -A hope_live.config.celery worker \
            --statedb worker -E --loglevel=DEBUG
        ;;
    beat)
        exec tini -- gosu hope:unicef celery -A hope_live.config.celery beat \
            --loglevel=DEBUG --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    flower)
        export DATABASE_URL="sqlite://:memory:"
        exec tini -- gosu hope:unicef celery -A hope_live.config.celery flower
        ;;
    *)
        exec "$@"
        ;;
esac
<<<<<<< Updated upstream

exec "$@"
