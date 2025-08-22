#!/usr/bin/env python3
"""
Kill existing server and start fresh
"""

import subprocess
import sys
import time
import os

def kill_existing_server():
    """Kill any existing server on port 8001."""
    try:
        # Find processes using port 8001
        result = subprocess.run(['lsof', '-ti:8001'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                print(f"🔄 Killing existing server process {pid}")
                subprocess.run(['kill', pid])
                time.sleep(1)
        else:
            print("✅ No existing server found on port 8001")
    except Exception as e:
        print(f"⚠️  Could not check for existing server: {e}")

def start_server():
    """Start the enhanced server."""
    print("🚀 Starting enhanced server...")
    try:
        # Start the server
        os.execv(sys.executable, [sys.executable, 'enhanced_server.py'])
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

if __name__ == "__main__":
    kill_existing_server()
    time.sleep(2)
    start_server()