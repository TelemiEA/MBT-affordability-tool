#!/usr/bin/env python3
"""
Standalone export functionality that definitely works
"""

import json
import csv
import os
from datetime import datetime

def export_results_now():
    """Export the current results immediately."""
    
    print("📊 STANDALONE EXPORT TOOL")
    print("=" * 50)
    
    # Load results
    results_file = "latest_automation_results.json"
    if not os.path.exists(results_file):
        print("❌ No results file found.")
        print("   Make sure you have run automation first.")
        return
    
    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded data with {len(data.get('results', {}))} scenarios")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = data.get('results', {})
    
    # 1. SIMPLE CSV EXPORT
    try:
        csv_filename = f"mbt_export_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            
            # Get all lender names first
            all_lenders = set()
            for scenario_data in results.values():
                lenders = scenario_data.get('lender_results', {})
                all_lenders.update(lenders.keys())
            all_lenders = sorted(list(all_lenders))
            
            # Create header
            header = [
                'Scenario ID', 'Description', 'Employment Type', 'Applicant Type',
                'Gen H Amount', 'Market Average', 'Gen H Rank', 'Total Lenders'
            ]
            
            # Add lender columns
            for lender in all_lenders:
                header.append(f'{lender}')
            
            writer = csv.writer(csvfile)
            writer.writerow(header)
            
            # Write data rows
            for scenario_id, scenario_data in results.items():
                stats = scenario_data.get('statistics', {})
                lenders = scenario_data.get('lender_results', {})
                
                # Determine types
                if 'joint' in scenario_id:
                    applicant_type = 'Joint'
                else:
                    applicant_type = 'Single'
                
                if 'self_employed' in scenario_id:
                    employment_type = 'Self-Employed'
                elif 'employed' in scenario_id:
                    employment_type = 'Employed'
                else:
                    employment_type = 'Mixed'
                
                # Basic row
                row = [
                    scenario_id,
                    scenario_data.get('description', ''),
                    employment_type,
                    applicant_type,
                    stats.get('gen_h_amount', 0),
                    int(stats.get('average', 0)),
                    stats.get('gen_h_rank', 0),
                    len(lenders)
                ]
                
                # Add lender amounts
                for lender in all_lenders:
                    row.append(lenders.get(lender, 0))
                
                writer.writerow(row)
        
        print(f"✅ CSV exported: {csv_filename}")
        
        # Show sample
        with open(csv_filename, 'r') as f:
            lines = f.readlines()[:3]
        print("   Sample rows:")
        for i, line in enumerate(lines):
            print(f"     {i+1}: {line.strip()[:80]}...")
            
    except Exception as e:
        print(f"❌ CSV export failed: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. SIMPLE JSON EXPORT
    try:
        json_filename = f"mbt_export_{timestamp}.json"
        
        export_data = {
            'export_info': {
                'export_date': datetime.now().isoformat(),
                'total_scenarios': len(results),
                'export_tool': 'standalone'
            },
            'summary': {
                'total_scenarios': len(results),
                'session_id': data.get('session_id', 'unknown'),
                'timestamp': data.get('timestamp', 'unknown')
            },
            'scenarios': {}
        }
        
        # Process each scenario
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
                'top_5_lenders': dict(sorted(lenders.items(), key=lambda x: x[1], reverse=True)[:5])
            }
        
        with open(json_filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ JSON exported: {json_filename}")
        
    except Exception as e:
        print(f"❌ JSON export failed: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. SUMMARY REPORT
    try:
        summary_filename = f"mbt_summary_{timestamp}.txt"
        
        with open(summary_filename, 'w') as f:
            f.write("MBT AFFORDABILITY BENCHMARKING SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Scenarios: {len(results)}\n")
            f.write(f"Session ID: {data.get('session_id', 'unknown')}\n\n")
            
            # Gen H Performance Summary
            gen_h_ranks = []
            gen_h_amounts = []
            
            f.write("GEN H PERFORMANCE BY SCENARIO\n")
            f.write("-" * 40 + "\n")
            
            for scenario_id, scenario_data in sorted(results.items()):
                stats = scenario_data.get('statistics', {})
                gen_h_amount = stats.get('gen_h_amount', 0)
                gen_h_rank = stats.get('gen_h_rank', 0)
                
                if gen_h_amount > 0:
                    gen_h_amounts.append(gen_h_amount)
                    if gen_h_rank > 0:
                        gen_h_ranks.append(gen_h_rank)
                
                description = scenario_data.get('description', scenario_id)[:50]
                f.write(f"{description:<52} £{gen_h_amount:>8,} (Rank: {gen_h_rank})\n")
            
            # Overall statistics
            if gen_h_amounts:
                f.write(f"\nOVERALL STATISTICS\n")
                f.write("-" * 20 + "\n")
                f.write(f"Average Gen H Amount: £{int(sum(gen_h_amounts)/len(gen_h_amounts)):,}\n")
                f.write(f"Highest Gen H Amount: £{max(gen_h_amounts):,}\n")
                f.write(f"Lowest Gen H Amount: £{min(gen_h_amounts):,}\n")
                
                if gen_h_ranks:
                    avg_rank = sum(gen_h_ranks) / len(gen_h_ranks)
                    f.write(f"Average Gen H Rank: {avg_rank:.1f}\n")
                    f.write(f"Best Gen H Rank: {min(gen_h_ranks)}\n")
                    f.write(f"Worst Gen H Rank: {max(gen_h_ranks)}\n")
        
        print(f"✅ Summary report: {summary_filename}")
        
    except Exception as e:
        print(f"❌ Summary report failed: {e}")
    
    print(f"\n🎉 Export completed successfully!")
    print(f"Files created in current directory:")
    if os.path.exists(csv_filename):
        print(f"   📄 CSV: {csv_filename}")
    if os.path.exists(json_filename):
        print(f"   📋 JSON: {json_filename}")  
    if os.path.exists(summary_filename):
        print(f"   📝 Summary: {summary_filename}")

if __name__ == "__main__":
    export_results_now()