#!/bin/bash
# setup_browsers.sh - Setup Playwright browsers for Railway deployment

echo "🔧 Setting up Playwright browsers for production deployment..."

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update -qq
apt-get install -qq -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libgtk-3-0 \
    libxss1 \
    fonts-liberation \
    xvfb

# Install Playwright browsers
echo "🌐 Installing Playwright Chromium browser..."
python3 -m playwright install chromium

# Install browser dependencies
echo "🔧 Installing Playwright browser dependencies..."
python3 -m playwright install-deps chromium

echo "✅ Playwright browser setup complete!"