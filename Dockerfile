FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency definitions
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy source code
COPY fastauth ./fastauth

# Run the application
CMD uv run fastapi run fastauth/main.py --port ${PORT:-8000} --host 0.0.0.0
