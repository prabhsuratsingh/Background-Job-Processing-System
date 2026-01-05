ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION}-slim

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:0.5.27 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# uv cache
RUN mkdir -p /cache/uv
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/cache/uv

# Create non-root user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install dependencies
RUN --mount=type=cache,target=/cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy project
COPY . /app

# Install project
RUN --mount=type=cache,target=/cache/uv \
    uv sync --frozen

# Permissions
RUN chown -R appuser:appuser /cache/uv /app

USER appuser

# Command is defined in docker-compose
CMD ["bash"]
