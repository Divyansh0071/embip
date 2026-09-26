# Production Dockerfile for EMBIP FastAPI Backend Engine
FROM python:3.12-slim

# Security & Python Environment Optimizations
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Set working directory
WORKDIR /app

# Install essential runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python package dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app /app/app

# Expose default HTTP port
EXPOSE 8000

# Non-root user execution for container security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Launch FastAPI application via Uvicorn
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
