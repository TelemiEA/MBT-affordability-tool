#!/bin/bash

# Install Playwright browsers
playwright install chromium
playwright install-deps

# Start the FastAPI application
uvicorn enhanced_server:app --host 0.0.0.0 --port $PORT