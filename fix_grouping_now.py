#!/usr/bin/env python3
"""
Force fix the grouping by creating a properly grouped results file
"""

import json

# Load the raw data
with open("latest_automation_results.json", 'r') as f:
    data = json.load(f)

print(f"Loaded {len(data['results'])} scenarios")

# Create grouped results manually
grouped_results = {
    'sole_employed': {},
    'sole_self_employed': {},
    'joint_employed': {},
    'joint_self_employed': {}
}

# Group each scenario
for scenario_id, scenario_data in data['results'].items():
    if scenario_id.startswith('single_employed'):
        grouped_results['sole_employed'][scenario_id] = scenario_data
    elif scenario_id.startswith('single_self_employed'):
        grouped_results['sole_self_employed'][scenario_id] = scenario_data
    elif scenario_id.startswith('joint_employed'):
        grouped_results['joint_employed'][scenario_id] = scenario_data
    elif scenario_id.startswith('joint_self_employed'):
        grouped_results['joint_self_employed'][scenario_id] = scenario_data

# Add grouping to the data
data['grouped_results'] = grouped_results
data['group_headers'] = {
    'sole_employed': 'Sole Applicant - Employed',
    'sole_self_employed': 'Sole Applicant - Self-Employed', 
    'joint_employed': 'Joint Applicants - Employed',
    'joint_self_employed': 'Joint Applicants - Self-Employed'
}

# Calculate summary statistics
all_ranks = []
rank_counts = {1: 0, 2: 0, 3: 0}
total_scenarios_with_ranks = 0

for scenario_data in data['results'].values():
    gen_h_rank = scenario_data.get('statistics', {}).get('gen_h_rank')
    if gen_h_rank and isinstance(gen_h_rank, int) and gen_h_rank > 0:
        all_ranks.append(gen_h_rank)
        total_scenarios_with_ranks += 1
        if gen_h_rank in rank_counts:
            rank_counts[gen_h_rank] += 1

data['summary_statistics'] = {
    'total_scenarios': len(data['results']),
    'scenarios_with_ranks': total_scenarios_with_ranks,
    'average_gen_h_rank': round(sum(all_ranks) / len(all_ranks), 2) if all_ranks else 0,
    'rank_percentages': {
        'rank_1_percent': round((rank_counts[1] / total_scenarios_with_ranks) * 100, 1) if total_scenarios_with_ranks > 0 else 0,
        'rank_2_percent': round((rank_counts[2] / total_scenarios_with_ranks) * 100, 1) if total_scenarios_with_ranks > 0 else 0,
        'rank_3_percent': round((rank_counts[3] / total_scenarios_with_ranks) * 100, 1) if total_scenarios_with_ranks > 0 else 0,
    },
    'top_3_percent': round(((rank_counts[1] + rank_counts[2] + rank_counts[3]) / total_scenarios_with_ranks) * 100, 1) if total_scenarios_with_ranks > 0 else 0
}

# Save the fixed file
with open("latest_automation_results.json", 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Fixed! Grouping added to latest_automation_results.json")
print("\nGroup counts:")
for group_key, scenarios in grouped_results.items():
    print(f"  {data['group_headers'][group_key]}: {len(scenarios)} scenarios")