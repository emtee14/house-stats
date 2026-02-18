FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

## System deps (keep minimal)
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    build-essential \

COPY pyproject.toml uv.lock* ./

RUN uv sync --no-dev

COPY ./app ./app

CMD ["uv", "run", "uvicorn", "app.main:create_app", "--host", "0.0.0.0", "--port", "8000"]