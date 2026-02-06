FROM python:3.13-slim-bookworm AS base_os
ARG GOSU_VERSION=1.17
ARG GOSU_SHA256=bbc4136d03ab138b1ad66fa4fc051bafc6cc7ffae632b069a53657279a450de3
ARG BUILD_DATE
ARG VERSION
ARG SOURCE_COMMIT

RUN set -x \
  && runtimeDeps=" \
    libmagic1 \
    libxml2 \
  " \
  && buildDeps=" \
wget \
" \
  && apt-get update && apt-get install -y --no-install-recommends ${buildDeps} ${runtimeDeps} \
  && rm -rf /var/lib/apt/lists/* \
  && wget --quiet -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-amd64" \
  && echo "$GOSU_SHA256 /usr/local/bin/gosu" | sha256sum --check --status \
  && chmod +x /usr/local/bin/gosu \
  && apt-get purge -y --auto-remove $buildDeps

RUN groupadd --gid 1024 unicef \
    && adduser --disabled-login --disabled-password --no-create-home --ingroup unicef -q hope


# ------- builder -------
FROM base_os AS builder
RUN set -x \
    && buildDeps="build-essential \
cmake \
curl \
gcc \
git \
libfontconfig1 \
libglib2.0-0 \
libssl-dev \
libxml2-dev  \
python3-dev \
zlib1g-dev  \
" \
    && apt-get update \
    && apt-get install -y --no-install-recommends $buildDeps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv uwsgi

# ------- tests -------
FROM builder AS tests
ARG BUILD_DATE
ARG SOURCE_COMMIT
ARG VERSION

LABEL distro="tests"
LABEL org.opencontainers.image.created="$BUILD_DATE"
LABEL org.opencontainers.image.version="$VERSION"

ENV PATH=/venv/bin:/usr/local/bin/:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=hope_live.config.settings \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    VIRTUAL_ENV=/venv \
    UWSGI_PROCESSES=4 \
    SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION:-0.0.0.dev0} \
    HATCH_BUILD_NO_HOOKS=1

WORKDIR /app
COPY uv.lock README.md MANIFEST.in pyproject.toml /app/
COPY src /app/src/

RUN --mount=type=cache,target=/root/.uv-cache \
    find ./src -name 'node_modules' -prune \
        -o -name *.py -o -name *.html -o -name *.js -o -name *.css \
        -type f \
        -exec ls -l "{}" \;  | sha1sum | awk '{print $1}' > CODE_CHECKSUM \
    && uv sync --cache-dir=/root/.uv-cache \
        --python=/usr/local/bin/python \
        --python-preference=system \
        --frozen --all-groups --verbose

# ------- production only deps-------
FROM builder AS production
ARG VERSION
ENV PATH=/venv/bin:/usr/local/bin/:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=hope_live.config.settings \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    VIRTUAL_ENV=/venv \
    UWSGI_PROCESSES=4 \
    SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION:-0.0.0.dev0} \
    HATCH_BUILD_NO_HOOKS=1

WORKDIR /app
COPY uv.lock README.md MANIFEST.in pyproject.toml /app/
COPY src /app/src/

RUN --mount=type=cache,target=/root/.uv-cache \
    uv sync --cache-dir=/root/.uv-cache \
        --python=/usr/local/bin/python \
        --python-preference=system \
        --frozen \
        --verbose



# ------- dist -------
FROM base_os AS dist
ARG BUILD_DATE
ARG SOURCE_COMMIT
ARG BRANCH
ARG GITHUB_SERVER_URL
ARG GITHUB_REPOSITORY

ENV PATH=/venv/bin:/usr/local/bin/:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=hope_live.config.settings \
    BUILD_DATE=$BUILD_DATE \
    SOURCE_COMMIT=$SOURCE_COMMIT \
    VERSION=$VERSION \
    BRANCH=$BRANCH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STATIC_URL="/static/" \
    PYTHONPATH=""\
    PGSSLCERT="/tmp/postgresql.crt" \
    UV_PROJECT_ENVIRONMENT=/venv \
    VIRTUAL_ENV=/venv \
    UWSGI_PROCESSES=4 \
    MEDIA_ROOT="/var/run/app/media" \
    STATIC_ROOT="/var/run/app/static" \
    SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION:-0.0.0.dev0} \
    HATCH_BUILD_NO_HOOKS=1

RUN <<EOF cat> /RELEASE
{"version": "$VERSION",
 "commit": "$SOURCE_COMMIT",
 "date": "$BUILD_DATE"
}
EOF
WORKDIR /app
COPY docker/conf /conf/
COPY docker/bin/* /usr/local/bin/

COPY . /app/

COPY --chown=hope:unicef --from=production /venv /venv
COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/uv /usr/local/bin/
RUN --mount=type=cache,target=/root/.uv-cache \
    uv --cache-dir=/root/.uv-cache  pip install --no-deps . \
    && rm -fr /app/*

EXPOSE 8000
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["run"]


LABEL maintainer="hope@unicef.org"
LABEL org.opencontainers.image.authors="hope@unicef.org"
LABEL org.opencontainers.image.description="Hope Live Dashboard"
LABEL org.opencontainers.image.documentation="https://github.com/unicef/hope-live-dashboard/"
LABEL org.opencontainers.image.title="Hope Live Dashboard"
LABEL org.opencontainers.image.licenses="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/blob/${SOURCE_COMMIT:-master}/LICENSE"
LABEL org.opencontainers.image.revision=$SOURCE_COMMIT
LABEL org.opencontainers.image.source="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/tree/${SOURCE_COMMIT:-master}/"
LABEL org.opencontainers.image.url="https://hub.docker.com/repository/docker/unicef/hope-live-dashboard/tags/"
LABEL org.opencontainers.image.vendor="UNICEF"
LABEL org.opencontainers.image.created="$BUILD_DATE"
LABEL org.opencontainers.image.version="$VERSION"
