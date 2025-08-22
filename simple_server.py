#!/usr/bin/env python3
"""
Simple test server for Railway deployment debugging
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
import uvicorn

app = FastAPI(title="MBT Tool - Railway Test")

@app.get("/")
async def root():
    return HTMLResponse("""
    <html>
        <body>
            <h1>🚀 MBT Tool is Live on Railway!</h1>
            <p>Server is working correctly.</p>
            <p>Port: {port}</p>
            <p>Environment: Railway</p>
        </body>
    </html>
    """.format(port=os.environ.get("PORT", "Not Set")))

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "port": os.environ.get("PORT", "Not Set"),
        "environment": "railway"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    print(f"🚀 Starting simple server on port {port}")
    print(f"🔧 Environment variables: PORT={port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)