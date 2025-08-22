#!/usr/bin/env python3
"""
Test the server export endpoint to make sure it's working
"""

import requests
import json
import time

def test_server_export():
    """Test the server export endpoints."""
    
    print("🔍 TESTING SERVER EXPORT ENDPOINTS")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # Check if server is running
    print("1. Checking server status...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is running")
        else:
            print(f"   ❌ Server responded with status {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("   ❌ Server is not running!")
        print("   💡 Start the server with: python enhanced_server.py")
        return
    except Exception as e:
        print(f"   ❌ Server connection error: {e}")
        return
    
    # Check if results are available
    print("\n2. Checking if automation results are available...")
    try:
        response = requests.get(f"{base_url}/api/latest-results", timeout=10)
        if response.status_code == 200:
            data = response.json()
            results_count = len(data.get('results', {}))
            print(f"   ✅ Results available: {results_count} scenarios")
            if results_count == 0:
                print("   ⚠️  No scenarios found - export may fail")
        else:
            print(f"   ❌ Results check failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Results check error: {e}")
    
    # Test export endpoints
    print("\n3. Testing export endpoints...")
    
    formats = ['csv', 'json', 'excel']
    
    for format_type in formats:
        print(f"\n   🧪 Testing {format_type.upper()} export...")
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}/api/export-data/{format_type}", timeout=30)
            elapsed = time.time() - start_time
            
            print(f"      Response time: {elapsed:.2f}s")
            print(f"      Status code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        print(f"      ✅ SUCCESS: {result.get('filename')} ({result.get('scenarios_exported', 0)} scenarios)")
                        print(f"      Message: {result.get('message', 'No message')}")
                    else:
                        print(f"      ❌ FAILED: {result.get('error', 'Unknown error')}")
                except json.JSONDecodeError:
                    print(f"      ❌ FAILED: Invalid JSON response")
                    print(f"      Response: {response.text[:200]}")
            else:
                print(f"      ❌ FAILED: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"      Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"      Response: {response.text[:200]}")
                    
        except requests.exceptions.Timeout:
            print(f"      ❌ TIMEOUT: Request took longer than 30 seconds")
        except Exception as e:
            print(f"      ❌ ERROR: {e}")
    
    print(f"\n🏁 SERVER EXPORT TEST COMPLETED")
    print("=" * 50)
    print("If all exports showed SUCCESS, your dashboard buttons should work!")
    print("If any failed, check the server console for detailed error messages.")

if __name__ == "__main__":
    test_server_export()