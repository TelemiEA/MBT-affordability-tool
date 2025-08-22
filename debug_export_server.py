#!/usr/bin/env python3
"""
Debug the export functionality by testing the server endpoint directly
"""

import requests
import json
import os

def test_export_endpoints():
    """Test the export endpoints directly."""
    
    print("🔍 DEBUGGING EXPORT ENDPOINTS")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Server is running: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Start with: python enhanced_server.py")
        return
    except Exception as e:
        print(f"❌ Server connection error: {e}")
        return
    
    # Check if results exist
    try:
        response = requests.get(f"{base_url}/api/latest-results", timeout=10)
        print(f"✅ Latest results endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results_count = len(data.get('results', {}))
            print(f"   Found {results_count} scenarios")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Latest results error: {e}")
        return
    
    # Test each export format
    formats = ['json', 'csv', 'excel']
    
    for format_type in formats:
        print(f"\n🧪 Testing {format_type.upper()} export...")
        try:
            response = requests.get(f"{base_url}/api/export-data/{format_type}", timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ {format_type.upper()} export successful: {result.get('filename')}")
                else:
                    print(f"   ❌ {format_type.upper()} export failed: {result}")
            else:
                print(f"   ❌ {format_type.upper()} export failed: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ {format_type.upper()} export error: {e}")
    
    print("\n📋 SUMMARY")
    print("-" * 20)
    print("If any exports failed, check the server logs for detailed error messages.")

def test_simple_manual_export():
    """Test a simple manual export without the server."""
    
    print("\n🔧 TESTING MANUAL EXPORT")
    print("=" * 50)
    
    # Check if results file exists
    if not os.path.exists("latest_automation_results.json"):
        print("❌ No results file found")
        return
    
    # Load data
    try:
        with open("latest_automation_results.json", 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data.get('results', {}))} scenarios")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Simple manual CSV export
    try:
        import csv
        from datetime import datetime
        
        filename = f"manual_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Scenario ID', 'Description', 'Gen H Amount', 'Market Average', 'Gen H Rank'])
            
            # Data
            for scenario_id, scenario_data in data.get('results', {}).items():
                stats = scenario_data.get('statistics', {})
                writer.writerow([
                    scenario_id,
                    scenario_data.get('description', ''),
                    stats.get('gen_h_amount', 0),
                    stats.get('average', 0),
                    stats.get('gen_h_rank', 0)
                ])
        
        print(f"✅ Manual CSV export successful: {filename}")
        
        # Show first few lines
        with open(filename, 'r') as f:
            lines = f.readlines()[:3]
        print("   First few lines:")
        for line in lines:
            print(f"     {line.strip()}")
            
        return filename
        
    except Exception as e:
        print(f"❌ Manual export failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test server endpoints
    test_export_endpoints()
    
    # Test manual export as backup
    test_simple_manual_export()