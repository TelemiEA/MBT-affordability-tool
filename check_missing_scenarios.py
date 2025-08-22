#!/usr/bin/env python3
"""
Check which scenarios are missing from the latest results
"""

import json

def check_missing_scenarios():
    """Check which scenarios are missing from latest results."""
    
    # Load latest results
    with open('latest_automation_results.json', 'r') as f:
        data = json.load(f)
    
    print('📊 SCENARIOS ANALYSIS')
    print('=' * 50)
    
    # Get scenarios that ran
    actual_scenarios = list(data['results'].keys())
    actual_scenarios.sort()
    
    print(f'✅ SCENARIOS THAT RAN ({len(actual_scenarios)}/32):')
    for s in actual_scenarios:
        print(f'  ✅ {s}')
    
    # Expected scenarios (all 32)
    expected_scenarios = [
        # Single employed (8)
        'single_employed_20k', 'single_employed_25k', 'single_employed_30k', 'single_employed_40k', 
        'single_employed_50k', 'single_employed_60k', 'single_employed_80k', 'single_employed_100k',
        
        # Single self-employed (8)  
        'single_self_employed_20k', 'single_self_employed_25k', 'single_self_employed_30k', 'single_self_employed_40k',
        'single_self_employed_50k', 'single_self_employed_60k', 'single_self_employed_80k', 'single_self_employed_100k',
        
        # Joint employed (8)
        'joint_employed_40k', 'joint_employed_50k', 'joint_employed_60k', 'joint_employed_80k',
        'joint_employed_100k', 'joint_employed_120k', 'joint_employed_160k', 'joint_employed_200k',
        
        # Joint self-employed (8)
        'joint_self_employed_40k', 'joint_self_employed_50k', 'joint_self_employed_60k', 'joint_self_employed_80k',
        'joint_self_employed_100k', 'joint_self_employed_120k', 'joint_self_employed_160k', 'joint_self_employed_200k'
    ]
    
    # Find missing scenarios
    missing = [s for s in expected_scenarios if s not in actual_scenarios]
    
    print(f'\n❌ MISSING SCENARIOS ({len(missing)}/32):')
    for s in missing:
        print(f'  ❌ {s}')
    
    # Group missing scenarios
    missing_groups = {
        'sole_employed': [s for s in missing if s.startswith('single_employed')],
        'sole_self_employed': [s for s in missing if s.startswith('single_self_employed')],
        'joint_employed': [s for s in missing if s.startswith('joint_employed')],
        'joint_self_employed': [s for s in missing if s.startswith('joint_self_employed')]
    }
    
    print(f'\n📋 MISSING BY GROUP:')
    for group_name, group_missing in missing_groups.items():
        if group_missing:
            print(f'  {group_name}: {len(group_missing)} missing')
            for s in group_missing:
                income = s.split('_')[-1]
                print(f'    - £{income}')
    
    print(f'\n🎯 SUMMARY:')
    print(f'  Total expected: 32 scenarios')
    print(f'  Successfully ran: {len(actual_scenarios)} scenarios')
    print(f'  Failed/Missing: {len(missing)} scenarios')
    print(f'  Success rate: {(len(actual_scenarios)/32*100):.1f}%')
    
    # Check specific scenarios you mentioned
    your_missing = ['single_employed_25k', 'single_self_employed_25k', 'joint_employed_200k']
    print(f'\n🔍 SPECIFIC SCENARIOS YOU MENTIONED:')
    for scenario in your_missing:
        status = '✅ RAN' if scenario in actual_scenarios else '❌ MISSING'
        print(f'  {scenario}: {status}')

if __name__ == "__main__":
    check_missing_scenarios()