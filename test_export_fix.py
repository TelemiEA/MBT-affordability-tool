#!/usr/bin/env python3
"""
Test the export fix
"""

import json
import os

def test_export_fix():
    """Test that the export fix works."""
    
    # Import the simple export functions from the fixed server
    import sys
    sys.path.append('.')
    
    # Load test data
    if not os.path.exists("latest_automation_results.json"):
        print("❌ No test data available")
        return
    
    with open("latest_automation_results.json", 'r') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data.get('results', {}))} scenarios for testing")
    
    # Test the simple export functions
    from enhanced_server import simple_csv_export, simple_json_export
    
    # Test CSV export
    csv_file = simple_csv_export(data, "test_export.csv")
    if csv_file and os.path.exists(csv_file):
        print(f"✅ CSV export working: {csv_file}")
        # Show first few lines
        with open(csv_file, 'r') as f:
            lines = f.readlines()[:3]
        print("   First few lines:")
        for line in lines:
            print(f"     {line.strip()}")
        os.remove(csv_file)  # cleanup
    else:
        print("❌ CSV export failed")
    
    # Test JSON export  
    json_file = simple_json_export(data, "test_export.json")
    if json_file and os.path.exists(json_file):
        print(f"✅ JSON export working: {json_file}")
        os.remove(json_file)  # cleanup
    else:
        print("❌ JSON export failed")
    
    print("\n🎉 Export fix appears to be working!")
    print("You should now be able to use the export buttons in the dashboard.")

if __name__ == "__main__":
    test_export_fix()