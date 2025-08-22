#!/usr/bin/env python3
"""
Simple export fix that doesn't require pandas or openpyxl
"""

import json
import csv
import os
from datetime import datetime

def simple_csv_export(data, filename=None):
    """Simple CSV export without pandas dependency."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mbt_results_{timestamp}.csv"
    
    try:
        results = data.get('results', {})
        if not results:
            print("❌ No results data to export")
            return None
        
        # Collect all unique lender names first
        all_lenders = set()
        for scenario_data in results.values():
            lenders = scenario_data.get('lender_results', {})
            all_lenders.update(lenders.keys())
        
        all_lenders = sorted(list(all_lenders))
        
        # Create CSV with all data
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'scenario_id', 'description', 'employment_type', 'applicant_type',
                'gen_h_amount', 'market_average', 'gen_h_rank', 'total_lenders'
            ] + [f'lender_{lender.replace(" ", "_").lower()}' for lender in all_lenders]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for scenario_id, scenario_data in results.items():
                stats = scenario_data.get('statistics', {})
                lenders = scenario_data.get('lender_results', {})
                
                # Basic row data
                row = {
                    'scenario_id': scenario_id,
                    'description': scenario_data.get('description', ''),
                    'employment_type': get_employment_type(scenario_id),
                    'applicant_type': get_applicant_type(scenario_id),
                    'gen_h_amount': stats.get('gen_h_amount', 0),
                    'market_average': stats.get('average', 0),
                    'gen_h_rank': stats.get('gen_h_rank', 0),
                    'total_lenders': len(lenders)
                }
                
                # Add lender amounts
                for lender in all_lenders:
                    field_name = f'lender_{lender.replace(" ", "_").lower()}'
                    row[field_name] = lenders.get(lender, 0)
                
                writer.writerow(row)
        
        print(f"✅ CSV exported successfully: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ CSV export failed: {e}")
        return None

def simple_json_export(data, filename=None):
    """Simple JSON export with formatting."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mbt_results_{timestamp}.json"
    
    try:
        # Add export metadata
        export_data = {
            'export_info': {
                'export_date': datetime.now().isoformat(),
                'total_scenarios': len(data.get('results', {})),
                'format_version': '1.0',
                'export_type': 'simple_json'
            },
            **data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ JSON exported successfully: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ JSON export failed: {e}")
        return None

def get_employment_type(scenario_id):
    """Determine employment type from scenario ID."""
    if 'employed' in scenario_id and 'self' not in scenario_id:
        return 'Employed'
    elif 'self_employed' in scenario_id:
        return 'Self-Employed'
    else:
        return 'Mixed' if 'joint' in scenario_id else 'Unknown'

def get_applicant_type(scenario_id):
    """Determine applicant type from scenario ID."""
    if scenario_id.startswith('single_'):
        return 'Single'
    elif scenario_id.startswith('joint_'):
        return 'Joint'
    else:
        return 'Unknown'

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

def main():
    """Test the simple export functions."""
    print("🔧 SIMPLE EXPORT TEST")
    print("=" * 50)
    
    # Load data
    data = load_latest_results()
    if not data:
        return
    
    print(f"✅ Loaded {len(data.get('results', {}))} scenarios")
    
    # Test exports
    csv_file = simple_csv_export(data)
    json_file = simple_json_export(data)
    
    print("\n📊 EXPORT SUMMARY")
    print("-" * 30)
    if csv_file:
        print(f"✅ CSV: {csv_file}")
    if json_file:
        print(f"✅ JSON: {json_file}")
    
    if csv_file or json_file:
        print("\n🎉 Export successful! Files are ready to use.")
    else:
        print("\n❌ Export failed.")

if __name__ == "__main__":
    main()