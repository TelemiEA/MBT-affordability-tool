#!/usr/bin/env python3
"""
Ultra-simple test server for Railway
"""

import os

try:
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully")
except Exception as e:
    print(f"❌ FastAPI import error: {e}")
    exit(1)

try:
    import uvicorn
    print("✅ Uvicorn imported successfully")
except Exception as e:
    print(f"❌ Uvicorn import error: {e}")
    exit(1)

app = FastAPI()

@app.get("/")
def read_root():
    port = os.environ.get("PORT", "Not Set")
    return {
        "message": "Server is working!",
        "port": port,
        "status": "success"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 8000))
        print(f"🚀 Starting server...")
        print(f"🔧 PORT from env: {os.environ.get('PORT', 'NOT SET')}")
        print(f"🔧 Using port: {port}")
        print(f"🔧 Host: 0.0.0.0")
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)