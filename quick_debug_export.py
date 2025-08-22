#!/usr/bin/env python3
"""
Quick debug to see exactly what's failing
"""

import requests
import json
import os

print("🔍 QUICK EXPORT DEBUG")
print("=" * 40)

# 1. Check if results file exists
results_file = "latest_automation_results.json"
if os.path.exists(results_file):
    print("✅ Results file exists")
    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
        print(f"✅ Results file loads: {len(data.get('results', {}))} scenarios")
    except Exception as e:
        print(f"❌ Results file error: {e}")
        exit()
else:
    print("❌ No results file found")
    exit()

# 2. Check server
print("\n🖥️  Checking server...")
try:
    response = requests.get("http://127.0.0.1:8001/health", timeout=3)
    print(f"✅ Server responding: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Server not running!")
    print("   Start with: python enhanced_server.py")
    exit()
except Exception as e:
    print(f"❌ Server error: {e}")
    exit()

# 3. Test export directly
print("\n📤 Testing CSV export...")
try:
    response = requests.get("http://127.0.0.1:8001/api/export-data/csv", timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"Response: {result}")
            if result.get('success'):
                print("✅ Export working!")
                print(f"   File: {result.get('filename')}")
                print(f"   Scenarios: {result.get('scenarios_exported')}")
            else:
                print(f"❌ Export failed: {result.get('error')}")
        except json.JSONDecodeError:
            print(f"❌ Invalid response: {response.text[:200]}")
    else:
        print(f"❌ HTTP error: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Request error: {e}")

# 4. Test manual export (should always work)
print("\n🔧 Testing manual export...")
try:
    import csv
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debug_export_{timestamp}.csv"
    
    results = data.get('results', {})
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Scenario', 'Gen_H_Amount', 'Description'])
        
        for scenario_id, scenario_data in list(results.items())[:3]:  # Just first 3 for test
            stats = scenario_data.get('statistics', {})
            writer.writerow([
                scenario_id,
                stats.get('gen_h_amount', 0),
                scenario_data.get('description', '')
            ])
    
    print(f"✅ Manual export works: {filename}")
    
except Exception as e:
    print(f"❌ Manual export failed: {e}")

print("\n🎯 SUMMARY:")
print("If server export failed, check the server console for detailed errors.")
print("If manual export worked, the issue is in the server endpoint code.")