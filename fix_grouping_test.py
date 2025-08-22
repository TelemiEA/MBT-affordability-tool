#!/usr/bin/env python3
"""
Test and fix the grouping function
"""

import json

def test_grouping():
    """Test if grouping works and fix if needed."""
    
    print("🔍 TESTING GROUPING FUNCTION")
    print("=" * 50)
    
    # Load the data
    with open("latest_automation_results.json", 'r') as f:
        data = json.load(f)
    
    print(f"📊 Loaded {len(data.get('results', {}))} scenarios")
    
    # Check scenario IDs
    scenario_ids = list(data.get('results', {}).keys())
    print(f"🔍 First 5 scenario IDs: {scenario_ids[:5]}")
    
    # Test the grouping logic manually
    grouped_results = {
        'sole_employed': {},
        'sole_self_employed': {},
        'joint_employed': {},
        'joint_self_employed': {}
    }
    
    for scenario_id, scenario_data in data['results'].items():
        print(f"Processing: {scenario_id}")
        
        # Determine scenario group based on actual scenario ID patterns
        if scenario_id.startswith('single_employed'):
            group = 'sole_employed'
            print(f"  -> Grouped as: {group}")
        elif scenario_id.startswith('single_self_employed'):
            group = 'sole_self_employed'
            print(f"  -> Grouped as: {group}")
        elif scenario_id.startswith('joint_employed'):
            group = 'joint_employed'
            print(f"  -> Grouped as: {group}")
        elif scenario_id.startswith('joint_self_employed'):
            group = 'joint_self_employed'
            print(f"  -> Grouped as: {group}")
        else:
            print(f"  -> ⚠️ Unknown scenario type: {scenario_id}")
            group = 'sole_employed'  # fallback
        
        grouped_results[group][scenario_id] = scenario_data
    
    # Print results
    print(f"\n📋 GROUP BREAKDOWN:")
    group_headers = {
        'sole_employed': 'Sole Applicant - Employed',
        'sole_self_employed': 'Sole Applicant - Self-Employed', 
        'joint_employed': 'Joint Applicants - Employed',
        'joint_self_employed': 'Joint Applicants - Self-Employed'
    }
    
    for group_key, scenarios in grouped_results.items():
        header = group_headers.get(group_key, group_key)
        print(f"  {header}: {len(scenarios)} scenarios")
        
        if scenarios:
            scenario_list = list(scenarios.keys())[:3]
            print(f"    Examples: {', '.join(scenario_list)}")
    
    # Create the enhanced data structure that should be returned
    enhanced_data = {
        **data,
        'grouped_results': grouped_results,
        'group_headers': group_headers
    }
    
    # Save it as the test output
    with open("fixed_grouped_results.json", 'w') as f:
        json.dump(enhanced_data, f, indent=2)
    
    print(f"\n💾 Enhanced data saved to fixed_grouped_results.json")
    print(f"✅ Grouping test completed!")

if __name__ == "__main__":
    test_grouping()