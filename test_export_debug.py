#!/usr/bin/env python3
"""
Debug export functionality to identify the issue
"""

import json
import os
import traceback

def debug_export_issue():
    """Debug what's causing the export to fail."""
    
    print("🔍 DEBUGGING EXPORT ISSUE")
    print("=" * 50)
    
    # Check if results file exists
    results_file = "latest_automation_results.json"
    if not os.path.exists(results_file):
        print(f"❌ Results file not found: {results_file}")
        return
    
    print(f"✅ Results file exists: {results_file}")
    
    # Try to load the file
    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
        print(f"✅ Successfully loaded JSON data")
        print(f"   Keys: {list(data.keys())}")
        print(f"   Results count: {len(data.get('results', {}))}")
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return
    
    # Test pandas availability
    try:
        import pandas as pd
        print("✅ Pandas is available")
    except ImportError as e:
        print(f"❌ Pandas not available: {e}")
        print("   Install with: pip install pandas")
        return
    
    # Test openpyxl availability
    try:
        import openpyxl
        print("✅ openpyxl is available")
    except ImportError as e:
        print(f"❌ openpyxl not available: {e}")
        print("   Install with: pip install openpyxl")
    
    # Try a simple CSV export test
    try:
        print("\n🧪 Testing simple CSV export...")
        
        # Create simple CSV data
        csv_data = []
        for scenario_id, scenario_data in data.get('results', {}).items():
            row = {
                'scenario_id': scenario_id,
                'description': scenario_data.get('description', ''),
            }
            csv_data.append(row)
        
        # Test DataFrame creation
        df = pd.DataFrame(csv_data)
        print(f"   DataFrame created with {len(df)} rows")
        
        # Test CSV export
        test_filename = "debug_export_test.csv"
        df.to_csv(test_filename, index=False)
        print(f"   ✅ CSV export successful: {test_filename}")
        
        # Clean up
        if os.path.exists(test_filename):
            os.remove(test_filename)
            print(f"   🧹 Cleaned up test file")
            
    except Exception as e:
        print(f"   ❌ CSV export test failed: {e}")
        traceback.print_exc()
    
    # Try the actual export function
    try:
        print("\n🧪 Testing actual export functions...")
        from export_data import export_to_csv, export_to_json
        
        # Test JSON export (simplest)
        json_result = export_to_json(data, "debug_test.json")
        if json_result:
            print(f"   ✅ JSON export worked: {json_result}")
            # Clean up
            if os.path.exists(json_result):
                os.remove(json_result)
        else:
            print(f"   ❌ JSON export failed")
        
        # Test CSV export
        csv_result = export_to_csv(data, "debug_test.csv")
        if csv_result:
            print(f"   ✅ CSV export worked: {csv_result}")
            # Clean up
            if os.path.exists(csv_result):
                os.remove(csv_result)
        else:
            print(f"   ❌ CSV export failed")
            
    except Exception as e:
        print(f"   ❌ Export function test failed: {e}")
        traceback.print_exc()
    
    # Test server export endpoint simulation
    try:
        print("\n🧪 Testing server export logic...")
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_filename = f"server_test_{timestamp}.json"
        
        with open(test_filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        if os.path.exists(test_filename):
            print(f"   ✅ Server-style export worked: {test_filename}")
            os.remove(test_filename)
        else:
            print(f"   ❌ Server-style export failed")
            
    except Exception as e:
        print(f"   ❌ Server export test failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_export_issue()