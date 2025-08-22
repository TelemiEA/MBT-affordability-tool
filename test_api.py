#!/usr/bin/env python3
"""
Test the API to see if grouping is working
"""

import requests
import json

def test_api():
    """Test if the API returns grouped results."""
    
    print("🔍 TESTING API GROUPING")
    print("=" * 50)
    
    try:
        # Test the API endpoint
        response = requests.get('http://127.0.0.1:8001/api/latest-results')
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ API Response received")
            print(f"📊 Keys in response: {list(data.keys())}")
            
            if 'grouped_results' in data:
                print("✅ grouped_results found!")
                grouped = data['grouped_results']
                print(f"🔍 Groups found: {list(grouped.keys())}")
                
                for group_key, scenarios in grouped.items():
                    print(f"  {group_key}: {len(scenarios)} scenarios")
            else:
                print("❌ grouped_results NOT found in response")
                
            if 'group_headers' in data:
                print("✅ group_headers found!")
                print(f"🏷️ Headers: {data['group_headers']}")
            else:
                print("❌ group_headers NOT found in response")
                
            if 'summary_statistics' in data:
                print("✅ summary_statistics found!")
                stats = data['summary_statistics']
                print(f"📈 Average rank: {stats.get('average_gen_h_rank')}")
            else:
                print("❌ summary_statistics NOT found in response")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_api()