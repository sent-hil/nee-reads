# Multi-stage Dockerfile for Nee Reads
# Stage 1: Build the frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/web

# Copy package files
COPY web/package.json web/package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source files
COPY web/ ./

# Build the frontend
RUN npm run build

# Stage 2: Python runtime
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy Python project files and README (required by hatchling)
COPY pyproject.toml README.md ./

# Copy application code
COPY api/ ./api/

# Install Python dependencies using uv
RUN uv sync --no-dev

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/web/dist ./web/dist

# Create data directory for database
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 7000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7000/api/books/search?q=test')" || exit 1

# Run the application using uv
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7000"]
