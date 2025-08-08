FROM python:3.9-slim

# 1. Install system dependencies with clean apt cache
RUN apt-get update && \
    apt-get install -y \
    wget \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    fonts-liberation \
    libglu1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Install Python dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Install Playwright browsers (Chromium only to save space)
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN python -m playwright install --with-deps chromium
RUN python -m playwright install-deps

# 4. Verify installation with proper Python syntax
RUN python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print(p.chromium.launch().version); p.stop()"

# 5. Copy app files
COPY . .

CMD ["gunicorn", "main:app"]