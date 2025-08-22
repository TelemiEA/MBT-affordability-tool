#!/usr/bin/env python3
"""
Test the grouping function to see if it's working correctly
"""

import json
import sys
sys.path.append('.')
from enhanced_server import enhance_results_with_grouping_and_stats

def test_grouping():
    """Test if the grouping function works correctly."""
    
    print("🔍 TESTING SCENARIO GROUPING")
    print("=" * 50)
    
    # Load the latest results
    try:
        with open("latest_automation_results.json", 'r') as f:
            data = json.load(f)
        
        print(f"📊 Loaded {len(data.get('results', {}))} scenarios")
        
        # Apply grouping
        enhanced_data = enhance_results_with_grouping_and_stats(data)
        
        # Check if grouping worked
        if 'grouped_results' in enhanced_data:
            print("✅ Grouping applied successfully!")
            
            grouped = enhanced_data['grouped_results']
            headers = enhanced_data.get('group_headers', {})
            
            print(f"\n📋 GROUP BREAKDOWN:")
            for group_key, scenarios in grouped.items():
                header = headers.get(group_key, group_key)
                print(f"  {header}: {len(scenarios)} scenarios")
                
                # Show first few scenario IDs in each group
                scenario_ids = list(scenarios.keys())[:3]
                if scenario_ids:
                    print(f"    Examples: {', '.join(scenario_ids)}")
                    
            # Check summary stats
            if 'summary_statistics' in enhanced_data:
                stats = enhanced_data['summary_statistics']
                print(f"\n📈 SUMMARY STATISTICS:")
                print(f"  Average Gen H rank: {stats.get('average_gen_h_rank', 'N/A')}")
                print(f"  Rank 1st: {stats.get('rank_percentages', {}).get('rank_1_percent', 0)}%")
                print(f"  Top 3: {stats.get('top_3_percent', 0)}%")
        else:
            print("❌ Grouping not applied - 'grouped_results' not found")
            print("Available keys:", list(enhanced_data.keys()))
            
    except Exception as e:
        print(f"❌ Error testing grouping: {e}")

if __name__ == "__main__":
    test_grouping()