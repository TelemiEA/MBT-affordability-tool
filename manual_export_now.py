#!/usr/bin/env python3
"""
Manual export that will definitely work
"""

import json
import csv
from datetime import datetime

# Load the data
print("Loading results...")
with open("latest_automation_results.json", 'r') as f:
    data = json.load(f)

results = data.get('results', {})
print(f"Found {len(results)} scenarios to export")

# Create timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 1. Create CSV Export
print("Creating CSV export...")
csv_filename = f"mbt_export_{timestamp}.csv"

# Get all unique lenders
all_lenders = set()
for scenario_data in results.values():
    lenders = scenario_data.get('lender_results', {})
    all_lenders.update(lenders.keys())
all_lenders = sorted(list(all_lenders))

print(f"Found {len(all_lenders)} unique lenders: {', '.join(all_lenders[:5])}...")

# Write CSV file
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # Create header
    header = ['Scenario_ID', 'Description', 'Gen_H_Amount', 'Market_Average', 'Gen_H_Rank', 'Total_Lenders']
    header.extend(all_lenders)
    writer.writerow(header)
    
    # Write data rows
    for scenario_id, scenario_data in results.items():
        stats = scenario_data.get('statistics', {})
        lenders = scenario_data.get('lender_results', {})
        
        row = [
            scenario_id,
            scenario_data.get('description', ''),
            stats.get('gen_h_amount', 0),
            int(stats.get('average', 0)),
            stats.get('gen_h_rank', 0),
            len(lenders)
        ]
        
        # Add lender amounts
        for lender in all_lenders:
            row.append(lenders.get(lender, 0))
        
        writer.writerow(row)

print(f"✅ CSV created: {csv_filename}")

# 2. Create JSON Export
print("Creating JSON export...")
json_filename = f"mbt_export_{timestamp}.json"

export_data = {
    'export_info': {
        'export_date': datetime.now().isoformat(),
        'total_scenarios': len(results),
        'session_id': data.get('session_id'),
        'original_timestamp': data.get('timestamp')
    },
    'summary': {
        'total_scenarios': len(results),
        'successful_scenarios': data.get('summary', {}).get('successful_scenarios', len(results))
    },
    'scenarios': {}
}

# Add scenario data
for scenario_id, scenario_data in results.items():
    stats = scenario_data.get('statistics', {})
    lenders = scenario_data.get('lender_results', {})
    
    export_data['scenarios'][scenario_id] = {
        'description': scenario_data.get('description', ''),
        'gen_h_amount': stats.get('gen_h_amount', 0),
        'market_average': int(stats.get('average', 0)),
        'gen_h_rank': stats.get('gen_h_rank', 0),
        'total_lenders': len(lenders),
        'lender_results': lenders,
        'top_5_lenders': dict(sorted(lenders.items(), key=lambda x: x[1], reverse=True)[:5]) if lenders else {}
    }

with open(json_filename, 'w', encoding='utf-8') as f:
    json.dump(export_data, f, indent=2)

print(f"✅ JSON created: {json_filename}")

# 3. Create Summary Report
print("Creating summary report...")
summary_filename = f"mbt_summary_{timestamp}.txt"

with open(summary_filename, 'w') as f:
    f.write("MBT AFFORDABILITY BENCHMARKING SUMMARY\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Session ID: {data.get('session_id', 'unknown')}\n")
    f.write(f"Total Scenarios: {len(results)}\n")
    f.write(f"Successful Scenarios: {data.get('summary', {}).get('successful_scenarios', len(results))}\n\n")
    
    # Gen H Performance Summary
    f.write("GEN H PERFORMANCE BY SCENARIO\n")
    f.write("-" * 50 + "\n")
    f.write(f"{'Scenario':<50} {'Gen H Amount':>12} {'Rank':>6}\n")
    f.write("-" * 68 + "\n")
    
    gen_h_amounts = []
    gen_h_ranks = []
    
    for scenario_id, scenario_data in sorted(results.items()):
        stats = scenario_data.get('statistics', {})
        gen_h_amount = stats.get('gen_h_amount', 0)
        gen_h_rank = stats.get('gen_h_rank', 0)
        
        if gen_h_amount > 0:
            gen_h_amounts.append(gen_h_amount)
            if gen_h_rank > 0:
                gen_h_ranks.append(gen_h_rank)
        
        description = scenario_data.get('description', scenario_id)[:48]
        f.write(f"{description:<50} £{gen_h_amount:>10,} {gen_h_rank:>6}\n")
    
    # Overall statistics
    if gen_h_amounts:
        f.write(f"\nOVERALL GEN H STATISTICS\n")
        f.write("-" * 30 + "\n")
        f.write(f"Average Amount: £{int(sum(gen_h_amounts)/len(gen_h_amounts)):,}\n")
        f.write(f"Highest Amount: £{max(gen_h_amounts):,}\n")
        f.write(f"Lowest Amount: £{min(gen_h_amounts):,}\n")
        
        if gen_h_ranks:
            avg_rank = sum(gen_h_ranks) / len(gen_h_ranks)
            f.write(f"Average Rank: {avg_rank:.1f}\n")
            f.write(f"Best Rank: {min(gen_h_ranks)}\n")
            f.write(f"Worst Rank: {max(gen_h_ranks)}\n")
    
    # Top performers by scenario type
    f.write(f"\nTOP PERFORMERS BY TYPE\n")
    f.write("-" * 30 + "\n")
    
    single_employed = [s for s in results.items() if 'single_employed' in s[0]]
    joint_employed = [s for s in results.items() if 'joint_employed' in s[0]]
    single_self = [s for s in results.items() if 'single_self_employed' in s[0]]
    joint_self = [s for s in results.items() if 'joint_self_employed' in s[0]]
    
    for category_name, category_scenarios in [
        ("Single Employed", single_employed),
        ("Joint Employed", joint_employed), 
        ("Single Self-Employed", single_self),
        ("Joint Self-Employed", joint_self)
    ]:
        if category_scenarios:
            best_scenario = max(category_scenarios, key=lambda x: x[1].get('statistics', {}).get('gen_h_amount', 0))
            best_amount = best_scenario[1].get('statistics', {}).get('gen_h_amount', 0)
            f.write(f"{category_name}: £{best_amount:,} ({best_scenario[1].get('description', '')})\n")

print(f"✅ Summary created: {summary_filename}")

print(f"\n🎉 EXPORT COMPLETED SUCCESSFULLY!")
print("=" * 50)
print(f"Files created:")
print(f"  📄 CSV Data: {csv_filename}")
print(f"  📋 JSON Data: {json_filename}")
print(f"  📝 Summary Report: {summary_filename}")
print(f"\nTotal scenarios exported: {len(results)}")

# Show first few lines of CSV as preview
print(f"\nPreview of CSV file:")
with open(csv_filename, 'r') as f:
    lines = f.readlines()[:3]
    for i, line in enumerate(lines, 1):
        preview = line.strip()[:100]
        print(f"  Line {i}: {preview}{'...' if len(line.strip()) > 100 else ''}")