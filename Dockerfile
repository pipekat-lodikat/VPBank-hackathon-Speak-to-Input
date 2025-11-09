# Production Dockerfile for VPBank Voice Agent - ECS Fargate
# Multi-stage build for optimized image size

FROM python:3.11-slim AS base

# Install system dependencies for Playwright and audio processing
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    # Playwright browser dependencies
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libxshmfence1 \
    fonts-liberation \
    libappindicator3-1 \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (required for browser-use)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy application code
COPY src ./src
COPY main_voice.py .
COPY main_browser_service.py .

# Copy .env file if exists (for local testing, use Secrets Manager in production)
COPY .env* ./

# Create non-root user for security best practices
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Create directories for runtime data
RUN mkdir -p /app/transcripts /app/logs && \
    chown -R appuser:appuser /app/transcripts /app/logs

USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=7860 \
    LOG_LEVEL=INFO

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose ports (7860 for voice bot, 7863 for browser agent)
EXPOSE 7860 7863

# Default command - can be overridden in ECS task definition
CMD ["python", "main_voice.py"]

