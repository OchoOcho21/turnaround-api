FROM python:3.9-slim

# 1. Install system dependencies + playwright browsers
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
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Install Python dependencies first (caching optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Install Playwright and browsers
RUN python -m playwright install
RUN python -m playwright install-deps

# 4. Copy app files
COPY . .

# 5. Set explicit browser path
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

CMD ["gunicorn", "main:app"]