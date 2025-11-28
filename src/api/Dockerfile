FROM python:3.13-slim

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
# Using --frozen for reproducible builds
# If network issues occur, the build will fail clearly and can be retried
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Default command
CMD ["uv", "run", "uvicorn", "person_tool.main:app", "--host", "0.0.0.0", "--port", "8000"]

