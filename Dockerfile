FROM python:3.12-slim

WORKDIR /backend

RUN apt-get update && apt-get install -y netcat-openbsd dos2unix curl && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc \
    && chmod +x /usr/local/bin/mc

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-root

COPY . .

RUN dos2unix /backend/scripts/entrypoint.sh && chmod +x /backend/scripts/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/backend/scripts/entrypoint.sh"]



