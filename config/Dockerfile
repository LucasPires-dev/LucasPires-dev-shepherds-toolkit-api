from python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock

run pip install poetry && / poetry config virtualenvs.create false && / poetry install --no-dev

copy . .

cmd ["gunicorn", "config.wssi:application", "--blind", "0.0.0.0:8000"]