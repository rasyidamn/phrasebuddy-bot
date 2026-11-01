FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY main.py ./
CMD ["uv", "run", "--no-dev", "main.py"]