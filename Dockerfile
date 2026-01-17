FROM python:3.12-alpine


WORKDIR /app


ENV POETRY_VERSION=2.1 POETRY_NO_INTERACTION=1 PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --only main

COPY . .

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]