#!/usr/bin/env python3
"""
Export MBT automation data to various formats
"""

import json
import csv
import pandas as pd
from datetime import datetime
import os

def load_latest_results():
    """Load the latest automation results."""
    try:
        if os.path.exists("latest_automation_results.json"):
            with open("latest_automation_results.json", 'r') as f:
                return json.load(f)
        else:
            print("❌ No results file found. Run automation first.")
            return None
    except Exception as e:
        print(f"❌ Error loading results: {e}")
        return None

def export_to_csv(data, filename=None):
    """Export results to CSV format."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mbt_results_{timestamp}.csv"
    
    try:
        csv_data = []
        
        for scenario_id, scenario_data in data.get('results', {}).items():
            # Basic scenario info
            row = {
                'scenario_id': scenario_id,
                'description': scenario_data.get('description', ''),
                'employment_type': get_employment_type(scenario_id),
                'applicant_type': get_applicant_type(scenario_id),
                'income_level': extract_income_from_description(scenario_data.get('description', ''))
            }
            
            # Statistics
            stats = scenario_data.get('statistics', {})
            row.update({
                'gen_h_amount': stats.get('gen_h_amount', 0),
                'market_average': stats.get('average', 0),
                'gen_h_difference': stats.get('gen_h_difference', 0),
                'gen_h_rank': stats.get('gen_h_rank', 0),
                'total_lenders': len(scenario_data.get('lender_results', {}))
            })
            
            # Individual lender results
            lenders = scenario_data.get('lender_results', {})
            for lender, amount in lenders.items():
                row[f'lender_{lender.lower().replace(" ", "_")}'] = amount
            
            csv_data.append(row)
        
        # Convert to DataFrame for easier CSV export
        df = pd.DataFrame(csv_data)
        df.to_csv(filename, index=False)
        
        print(f"✅ CSV exported: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error exporting CSV: {e}")
        return None

def export_to_excel(data, filename=None):
    """Export results to Excel format with multiple sheets."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mbt_results_{timestamp}.xlsx"
    
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            
            # Sheet 1: Summary Overview
            summary_data = []
            for scenario_id, scenario_data in data.get('results', {}).items():
                stats = scenario_data.get('statistics', {})
                summary_data.append({
                    'Scenario': scenario_data.get('description', scenario_id),
                    'Employment Type': get_employment_type(scenario_id),
                    'Applicant Type': get_applicant_type(scenario_id),
                    'Income': extract_income_from_description(scenario_data.get('description', '')),
                    'Gen H Amount': f"£{stats.get('gen_h_amount', 0):,}",
                    'Market Average': f"£{stats.get('average', 0):,.0f}",
                    'Gen H Rank': stats.get('gen_h_rank', 'N/A'),
                    'Total Lenders': len(scenario_data.get('lender_results', {})),
                    'Performance vs Average': f"{'+'if stats.get('gen_h_difference', 0) >= 0 else ''}£{stats.get('gen_h_difference', 0):,.0f}"
                })
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet 2: Detailed Lender Results
            detailed_data = []
            for scenario_id, scenario_data in data.get('results', {}).items():
                lenders = scenario_data.get('lender_results', {})
                sorted_lenders = sorted(lenders.items(), key=lambda x: x[1], reverse=True)
                
                for rank, (lender, amount) in enumerate(sorted_lenders, 1):
                    detailed_data.append({
                        'Scenario': scenario_data.get('description', scenario_id),
                        'Lender': lender,
                        'Amount': amount,
                        'Formatted Amount': f"£{amount:,}",
                        'Rank in Scenario': rank,
                        'Employment Type': get_employment_type(scenario_id),
                        'Applicant Type': get_applicant_type(scenario_id)
                    })
            
            df_detailed = pd.DataFrame(detailed_data)
            df_detailed.to_excel(writer, sheet_name='Detailed Results', index=False)
            
            # Sheet 3: Gen H Performance Analysis
            gen_h_data = []
            for scenario_id, scenario_data in data.get('results', {}).items():
                stats = scenario_data.get('statistics', {})
                gen_h_amount = stats.get('gen_h_amount', 0)
                
                if gen_h_amount > 0:
                    gen_h_data.append({
                        'Scenario': scenario_data.get('description', scenario_id),
                        'Gen H Amount': f"£{gen_h_amount:,}",
                        'Rank': stats.get('gen_h_rank', 'N/A'),
                        'Difference vs Average': f"{'+'if stats.get('gen_h_difference', 0) >= 0 else ''}£{stats.get('gen_h_difference', 0):,.0f}",
                        'Performance': 'Above Average' if stats.get('gen_h_difference', 0) > 0 else 'Below Average' if stats.get('gen_h_difference', 0) < 0 else 'At Average',
                        'Employment Type': get_employment_type(scenario_id),
                        'Income Level': extract_income_from_description(scenario_data.get('description', ''))
                    })
            
            df_gen_h = pd.DataFrame(gen_h_data)
            df_gen_h.to_excel(writer, sheet_name='Gen H Analysis', index=False)
            
            # Sheet 4: Statistics Summary
            if 'summary_statistics' in data:
                stats_summary = data['summary_statistics']
                stats_data = [
                    ['Total Scenarios', stats_summary.get('total_scenarios', 0)],
                    ['Average Gen H Rank', stats_summary.get('average_gen_h_rank', 'N/A')],
                    ['Ranked 1st (%)', f"{stats_summary.get('rank_percentages', {}).get('rank_1_percent', 0)}%"],
                    ['Ranked 2nd (%)', f"{stats_summary.get('rank_percentages', {}).get('rank_2_percent', 0)}%"],
                    ['Ranked 3rd (%)', f"{stats_summary.get('rank_percentages', {}).get('rank_3_percent', 0)}%"],
                    ['Top 3 Overall (%)', f"{stats_summary.get('top_3_percent', 0)}%"],
                    ['Export Date', datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                ]
                
                df_stats = pd.DataFrame(stats_data, columns=['Metric', 'Value'])
                df_stats.to_excel(writer, sheet_name='Statistics', index=False)
        
        print(f"✅ Excel exported: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error exporting Excel: {e}")
        return None

def export_to_json(data, filename=None):
    """Export results to formatted JSON."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mbt_results_{timestamp}.json"
    
    try:
        # Add export metadata
        export_data = {
            'export_info': {
                'export_date': datetime.now().isoformat(),
                'total_scenarios': len(data.get('results', {})),
                'format_version': '1.0'
            },
            **data
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ JSON exported: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error exporting JSON: {e}")
        return None

def get_employment_type(scenario_id):
    """Determine employment type from scenario ID."""
    if 'employed' in scenario_id:
        return 'Employed'
    elif 'self_employed' in scenario_id:
        return 'Self-Employed'
    else:
        return 'Unknown'

def get_applicant_type(scenario_id):
    """Determine applicant type from scenario ID."""
    if scenario_id.startswith('single_'):
        return 'Single'
    elif scenario_id.startswith('joint_'):
        return 'Joint'
    else:
        return 'Unknown'

def extract_income_from_description(description):
    """Extract income amount from description."""
    import re
    match = re.search(r'£(\d+)k', description)
    if match:
        return f"£{match.group(1)}k"
    return 'Unknown'

def export_all_formats(data=None):
    """Export data in all available formats."""
    if data is None:
        data = load_latest_results()
    
    if not data:
        return
    
    print("📊 EXPORTING MBT RESULTS")
    print("=" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export to all formats
    csv_file = export_to_csv(data, f"mbt_results_{timestamp}.csv")
    excel_file = export_to_excel(data, f"mbt_results_{timestamp}.xlsx")
    json_file = export_to_json(data, f"mbt_results_{timestamp}.json")
    
    print(f"\n✅ Export completed!")
    if csv_file:
        print(f"   📄 CSV: {csv_file}")
    if excel_file:
        print(f"   📊 Excel: {excel_file}")
    if json_file:
        print(f"   📋 JSON: {json_file}")
    
    return {
        'csv': csv_file,
        'excel': excel_file, 
        'json': json_file
    }

def main():
    """Main function for command line usage."""
    import sys
    
    if len(sys.argv) > 1:
        format_type = sys.argv[1].lower()
        data = load_latest_results()
        if not data:
            return
        
        if format_type == 'csv':
            export_to_csv(data)
        elif format_type == 'excel':
            export_to_excel(data)
        elif format_type == 'json':
            export_to_json(data)
        elif format_type == 'all':
            export_all_formats(data)
        else:
            print("Usage: python3 export_data.py [csv|excel|json|all]")
    else:
        # Default: export all formats
        export_all_formats()

if __name__ == "__main__":
    main()