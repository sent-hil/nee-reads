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

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy Python project files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir .

# Copy application code
COPY api/ ./api/

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

# Run the application
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7000"]
