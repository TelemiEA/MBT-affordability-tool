"""
Test Single API Call - Test one scenario through the API
"""

import asyncio
import requests
import json

async def test_single_api_call():
    """Test a single API call to verify the automation works."""
    
    print("🧪 TESTING SINGLE API SCENARIO")
    print("=" * 40)
    
    # Test the test automation endpoint first (single scenario)
    try:
        print("1. Testing single scenario endpoint...")
        response = requests.get("http://127.0.0.1:8001/api/test-automation", timeout=300)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Single scenario test successful!")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            
            # Check if we have test_result
            if 'test_result' in data:
                test_result = data['test_result']
                lenders_data = test_result.get('lenders_data', {})
                print(f"💰 Lenders found: {len(lenders_data)}")
                
                for lender, amount in list(lenders_data.items())[:5]:  # Show first 5
                    if isinstance(amount, int):
                        print(f"   {lender}: £{amount:,}")
                    else:
                        print(f"   {lender}: {amount}")
            
        else:
            print(f"❌ Single scenario test failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Single scenario test error: {e}")
    
    print("\n" + "=" * 40)
    
    # Now test the sample scenarios endpoint
    try:
        print("2. Testing sample scenarios endpoint...")
        response = requests.get("http://127.0.0.1:8001/api/run-sample-scenarios", timeout=600)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sample scenarios successful!")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            print(f"Results count: {len(data.get('results', {}))}")
            
        else:
            print(f"❌ Sample scenarios failed: {response.status_code}")
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"Error: {error_data}")
            
    except Exception as e:
        print(f"❌ Sample scenarios error: {e}")

if __name__ == "__main__":
    asyncio.run(test_single_api_call())