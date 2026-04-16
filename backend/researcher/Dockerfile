# Build from backend/: docker build -f researcher/Dockerfile .
# Includes backend/lll_model.py (shared with other services) + researcher app.

FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies (system-level dependencies for Chromium)
RUN npx -y playwright install --with-deps chromium

# Install Python package manager
RUN pip install uv

# Researcher package metadata and lockfile
COPY researcher/pyproject.toml researcher/uv.lock ./

# Install Python dependencies during build
RUN uv sync --frozen --no-install-project

# Shared model helper (single source: backend/lll_model.py) + researcher modules
COPY lll_model.py ./
COPY researcher/*.py ./

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
