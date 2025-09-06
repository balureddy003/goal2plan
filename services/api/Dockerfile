FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Copy and install decision kernel first (shared local package)
COPY services/decision_kernel /tmp/decision_kernel
RUN pip install -e /tmp/decision_kernel

# Copy API and install
COPY services/api/pyproject.toml /app/services/api/pyproject.toml
RUN pip install -e /app/services/api

# Copy app source (after deps for better caching)
COPY services/api/app /app/services/api/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "services/api/app"]

