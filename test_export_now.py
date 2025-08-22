#!/usr/bin/env python3
"""
Test export with the debug server
"""

import subprocess
import time
import requests
import json
import os

def main():
    print("🧪 TESTING EXPORT WITH DEBUG OUTPUT")
    print("=" * 50)
    
    # Check if results exist
    if not os.path.exists("latest_automation_results.json"):
        print("❌ No results file found")
        return
    
    print("✅ Results file exists")
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8001/health", timeout=2)
        print("✅ Server is running")
    except:
        print("❌ Server not running - start it first with: python enhanced_server.py")
        return
    
    # Test CSV export with debug output
    print("\n📤 Testing CSV export (watch server console for debug output)...")
    
    try:
        response = requests.get("http://127.0.0.1:8001/api/export-data/csv", timeout=15)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ SUCCESS!")
                print(f"   Response: {result}")
                
                # Check if file exists
                filename = result.get('filename')
                if filename and os.path.exists(filename):
                    size = os.path.getsize(filename)
                    print(f"   File created: {filename} ({size} bytes)")
                    
                    # Show first few lines
                    with open(filename, 'r') as f:
                        lines = f.readlines()[:3]
                    print("   First lines:")
                    for line in lines:
                        print(f"     {line.strip()}")
                else:
                    print("   ⚠️ File not found on disk")
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response")
                print(f"   Raw response: {response.text}")
        else:
            print(f"❌ HTTP Error {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n💡 Check the server console above for detailed debug output!")

if __name__ == "__main__":
    main()