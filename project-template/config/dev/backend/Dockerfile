FROM python:3.10.5

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN echo "APT::Install-Recommends \"0\";" >> /etc/apt/apt.conf.d/02recommends && \
    echo "APT::Install-Suggests \"0\";" >> /etc/apt/apt.conf.d/02recommends && \
    apt-get -qq update && \
    apt-get -qq install \
        build-essential \
        && \
    rm -rf /var/lib/apt/lists/* && \
    true

RUN pip install poetry==1.1.13

# Requirements are installed here to ensure they will be cached.
# Turns off virtualenv mode so the deps are installed globally in the container.
COPY ./pyproject.toml ./poetry.lock /app/
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root --no-ansi
