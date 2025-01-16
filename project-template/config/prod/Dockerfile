# Build assets and fetch dependencies here
FROM python:3.12 AS build

ARG PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    # poetry
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN set -ex \
    && pip install --upgrade pip \
    && pip install poetry==2.0.1

# Install node
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs

COPY pyproject.toml poetry.lock /app/
COPY package.json package-lock.json vite.config.mjs /app/

COPY scripts/ /app/scripts/
COPY main/ /app/main/
COPY manage.py /app/manage.py

RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && poetry install --sync --no-root --without dev

RUN npm ci && npm cache clear --force && npm run build:assets

RUN . /opt/venv/bin/activate \
    && SECRET_KEY=build /app/manage.py collectstatic

# Creates the minimum necessary image to execute the service.
FROM python:3.12 AS runtime

ARG APP_VERSION=development

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx libpq5 xz-utils

# Setup s6 as init system
ARG S6_OVERLAY_VERSION=3.2.0.2

ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz
ENTRYPOINT ["/init"]
COPY config/prod/s6-overlay/ /etc/s6-overlay/

# Setup nginx
RUN rm /etc/nginx/sites-enabled/default
COPY config/prod/nginx.conf /etc/nginx/sites-available/app.conf
RUN ln -s /etc/nginx/sites-available/app.conf /etc/nginx/sites-enabled/app.conf

# Set up the app
COPY config/prod/start.sh /app/
COPY manage.py /app/

COPY --from=build /opt/venv/ /opt/venv/
COPY --from=build /app/main/ /app/main/
COPY --from=build /app/static/ /app/static/

CMD ["/app/start.sh"]

RUN echo $APP_VERSION > /app/version

# Set up a user for the app and give it read-only access to the code
# Nginx needs to start as root to bind port 80 (and will then drop worker processes to 'nobody' user)
# So we'll drop just the Python app's user to 'app' using the s6 service script
RUN groupadd app && \
    # TODO: See supervisord.conf for why I need the home directory
    useradd app -m -g app && \
    # Give our gunicorn user read-only access to Python
    chown -R root:app /app && \
    chmod -R 750 /app && \
    # Move this to a separate folder so Nginx doesn't need to have any access to the Python files.
    # So if it gets compromised, an attacker can't read out our code.
    # cp for /app/static/ so staticfiles.json can still be accessed by Django
    cp -r /app/static/ /app-static/ && \
    chown -R root:www-data /app-static/ && \
    chmod -R 750 /app-static/
