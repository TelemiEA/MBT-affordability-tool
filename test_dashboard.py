"""
Test Dashboard Access
"""
import requests

def test_dashboard():
    """Test dashboard endpoints."""
    base_url = "http://127.0.0.1:8001"
    
    print("🧪 Testing Dashboard Access")
    print("=" * 40)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health error: {e}")
    
    # Test status endpoint  
    try:
        response = requests.get(f"{base_url}/api/status")
        print(f"✅ Status: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Status error: {e}")
    
    # Test dashboard endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Dashboard: {response.status_code}")
        if response.status_code == 200:
            print("✅ Dashboard accessible!")
            print(f"Content length: {len(response.text)} characters")
        else:
            print(f"❌ Dashboard error: {response.status_code}")
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
    
    # Test automation endpoint
    try:
        print("\n🧪 Testing automation endpoints...")
        response = requests.get(f"{base_url}/api/latest-results")
        print(f"Latest results: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Results available: {data.get('status', 'unknown')}")
        else:
            print(f"⚠️ No results yet: {response.status_code}")
    except Exception as e:
        print(f"❌ Results error: {e}")

if __name__ == "__main__":
    test_dashboard()