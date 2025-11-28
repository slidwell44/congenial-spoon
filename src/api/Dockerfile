FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Default command
CMD ["uv", "run", "uvicorn", "person_tool.main:app", "--host", "0.0.0.0", "--port", "8000"]

