#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

# Create a simple FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse("""
    <html>
        <head><title>Test Server</title></head>
        <body>
            <h1>🚀 Server is Working!</h1>
            <p>If you can see this, the server is running correctly.</p>
            <p><a href="/test">Test endpoint</a></p>
        </body>
    </html>
    """)

@app.get("/test")
async def test():
    return {"message": "Test endpoint working!", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("🚀 Starting simple test server...")
    print("📱 Access at: http://127.0.0.1:8003")
    print("📱 Or try: http://localhost:8003")
    
    uvicorn.run(
        app, 
        host="0.0.0.0",  # Listen on all interfaces
        port=8003,
        log_level="info"
    )