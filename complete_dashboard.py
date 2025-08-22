#!/usr/bin/env python3
"""
Complete MBT Dashboard Generator - Original Format
Recreates the full horizontal layout with all lenders and summary stats
"""

import json
import os
from datetime import datetime
from collections import defaultdict

def calculate_summary_stats(results_data):
    """Calculate Gen H performance summary statistics."""
    if not results_data or 'results' not in results_data:
        return {"average_rank": "N/A", "pct_ranked_1st": "N/A", "pct_ranked_top3": "N/A", "total_scenarios": 0}
    
    ranks = []
    ranked_1st = 0
    ranked_top3 = 0
    
    for scenario_data in results_data['results'].values():
        if 'statistics' in scenario_data:
            rank = scenario_data['statistics'].get('gen_h_rank')
            if rank and isinstance(rank, int):
                ranks.append(rank)
                if rank == 1:
                    ranked_1st += 1
                if rank <= 3:
                    ranked_top3 += 1
    
    total_scenarios = len(ranks)
    if total_scenarios == 0:
        return {"average_rank": "N/A", "pct_ranked_1st": "N/A", "pct_ranked_top3": "N/A", "total_scenarios": 0}
    
    average_rank = sum(ranks) / len(ranks)
    pct_1st = (ranked_1st / total_scenarios) * 100
    pct_top3 = (ranked_top3 / total_scenarios) * 100
    
    return {
        "average_rank": round(average_rank, 1),
        "pct_ranked_1st": round(pct_1st, 1),
        "pct_ranked_top3": round(pct_top3, 1),
        "total_scenarios": total_scenarios
    }

def group_scenarios_by_income(results_data):
    """Group scenarios by income level and employment type."""
    if not results_data or 'results' not in results_data:
        return {}
    
    grouped = defaultdict(lambda: defaultdict(dict))
    
    # Income level mapping
    income_mapping = {
        "20k": "£20,000",
        "25k": "£25,000", 
        "30k": "£30,000",
        "40k": "£40,000",
        "50k": "£50,000",
        "60k": "£60,000",
        "80k": "£80,000",
        "100k": "£100,000",
        "120k": "£120,000",
        "160k": "£160,000",
        "200k": "£200,000"
    }
    
    for scenario_id, scenario_data in results_data['results'].items():
        # Parse scenario details
        if "joint" in scenario_id:
            applicant_type = "Joint"
        else:
            applicant_type = "Single"
            
        if "self_employed" in scenario_id:
            employment_type = "Self-Employed"
        else:
            employment_type = "Employed"
            
        # Extract income level
        income_level = None
        for income_key, income_display in income_mapping.items():
            if income_key in scenario_id:
                income_level = income_display
                break
        
        if income_level:
            key = f"{applicant_type} {employment_type}"
            grouped[income_level][key] = scenario_data
    
    return dict(grouped)

def get_all_lenders(results_data):
    """Get all unique lenders across all scenarios."""
    if not results_data or 'results' not in results_data:
        return []
    
    all_lenders = set()
    for scenario_data in results_data['results'].values():
        lender_results = scenario_data.get('lender_results', {})
        all_lenders.update(lender_results.keys())
    
    # Sort lenders alphabetically, but put Gen H first
    lenders = sorted(list(all_lenders))
    if 'Gen H' in lenders:
        lenders.remove('Gen H')
        lenders.insert(0, 'Gen H')
    
    return lenders

def create_complete_dashboard(results_data):
    """Create the complete dashboard HTML matching the original format."""
    
    # Calculate summary statistics
    summary_stats = calculate_summary_stats(results_data)
    
    # Group scenarios
    grouped_scenarios = group_scenarios_by_income(results_data)
    
    # Get all lenders
    all_lenders = get_all_lenders(results_data)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MBT Affordability Benchmarking Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.8rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .summary-stats {{
            display: flex;
            justify-content: space-around;
            background: #f8fafc;
            border-bottom: 3px solid #e2e8f0;
            padding: 30px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #1e293b;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #64748b;
            font-weight: 500;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .income-section {{
            border-bottom: 2px solid #f1f5f9;
        }}
        
        .income-header {{
            background: #1e293b;
            color: white;
            padding: 15px 30px;
            font-size: 1.3rem;
            font-weight: 600;
        }}
        
        .scenarios-container {{
            padding: 0;
        }}
        
        .scenario-group {{
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .scenario-header {{
            background: #f8fafc;
            padding: 12px 30px;
            font-weight: 600;
            color: #374151;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .lender-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .lender-table th {{
            background: #f9fafb;
            padding: 12px 8px;
            text-align: center;
            font-weight: 600;
            color: #374151;
            border: 1px solid #e5e7eb;
            font-size: 0.85rem;
        }}
        
        .lender-table td {{
            padding: 10px 8px;
            text-align: center;
            border: 1px solid #e5e7eb;
            font-size: 0.85rem;
        }}
        
        .lender-table tbody tr:hover {{
            background: #f9fafb;
        }}
        
        .gen-h-cell {{
            background: linear-gradient(135deg, #10b981, #059669) !important;
            color: white !important;
            font-weight: bold !important;
        }}
        
        .amount-cell {{
            font-weight: 600;
            color: #059669;
        }}
        
        .rank-1 {{ background: #fef3c7; color: #92400e; font-weight: bold; }}
        .rank-2 {{ background: #f3f4f6; color: #374151; font-weight: bold; }}
        .rank-3 {{ background: #fef2f2; color: #991b1b; font-weight: bold; }}
        .rank-other {{ background: #f8fafc; color: #6b7280; }}
        
        .refresh-controls {{
            padding: 20px 30px;
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
            text-align: center;
        }}
        
        .refresh-btn {{
            background: linear-gradient(135deg, #059669, #047857);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            margin: 0 10px;
            transition: all 0.3s ease;
        }}
        
        .refresh-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(5, 150, 105, 0.4);
        }}
        
        .timestamp {{
            text-align: center;
            color: #64748b;
            font-size: 0.9rem;
            margin-top: 15px;
        }}
        
        .no-data {{
            text-align: center;
            padding: 60px;
            color: #6b7280;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🏠 MBT Affordability Benchmarking</h1>
            <p>Comprehensive mortgage lending comparison across all major lenders</p>
        </div>
        
        <div class="summary-stats">
            <div class="stat-item">
                <div class="stat-value">{summary_stats['average_rank']}</div>
                <div class="stat-label">Average Rank</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{summary_stats['pct_ranked_1st']}%</div>
                <div class="stat-label">Ranked 1st</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{summary_stats['pct_ranked_top3']}%</div>
                <div class="stat-label">Ranked Top 3</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{summary_stats['total_scenarios']}</div>
                <div class="stat-label">Total Scenarios</div>
            </div>
        </div>
"""

    # Add income sections
    if grouped_scenarios:
        # Sort income levels
        income_order = ["£20,000", "£25,000", "£30,000", "£40,000", "£50,000", "£60,000", "£80,000", "£100,000", "£120,000", "£160,000", "£200,000"]
        
        for income_level in income_order:
            if income_level in grouped_scenarios:
                scenarios = grouped_scenarios[income_level]
                
                html_content += f"""
        <div class="income-section">
            <div class="income-header">{income_level} Income Scenarios</div>
            <div class="scenarios-container">
"""
                
                # Scenario type order
                scenario_order = ["Single Employed", "Single Self-Employed", "Joint Employed", "Joint Self-Employed"]
                
                for scenario_type in scenario_order:
                    if scenario_type in scenarios:
                        scenario_data = scenarios[scenario_type]
                        lender_results = scenario_data.get('lender_results', {})
                        statistics = scenario_data.get('statistics', {})
                        
                        html_content += f"""
                <div class="scenario-group">
                    <div class="scenario-header">{scenario_type}</div>
                    <table class="lender-table">
                        <thead>
                            <tr>
                                <th>Metric</th>
"""
                        
                        # Add lender headers
                        for lender in all_lenders:
                            html_content += f'<th>{lender}</th>'
                        
                        html_content += """
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>Amount</strong></td>
"""
                        
                        # Add amounts for each lender
                        for lender in all_lenders:
                            amount = lender_results.get(lender, 'N/A')
                            if amount and amount != 'N/A':
                                try:
                                    amount_formatted = f"£{int(amount):,}"
                                except:
                                    amount_formatted = str(amount)
                            else:
                                amount_formatted = 'N/A'
                            
                            cell_class = "amount-cell"
                            if lender == "Gen H" and amount != 'N/A':
                                cell_class += " gen-h-cell"
                            
                            html_content += f'<td class="{cell_class}">{amount_formatted}</td>'
                        
                        html_content += """
                            </tr>
                            <tr>
                                <td><strong>Rank</strong></td>
"""
                        
                        # Calculate ranks for all lenders
                        sorted_lenders = sorted(lender_results.items(), key=lambda x: x[1] if x[1] != 'N/A' else 0, reverse=True)
                        lender_ranks = {lender: i+1 for i, (lender, amount) in enumerate(sorted_lenders) if amount != 'N/A'}
                        
                        # Add ranks for each lender
                        for lender in all_lenders:
                            rank = lender_ranks.get(lender, 'N/A')
                            if rank != 'N/A':
                                if rank == 1:
                                    rank_class = "rank-1"
                                elif rank == 2:
                                    rank_class = "rank-2"
                                elif rank == 3:
                                    rank_class = "rank-3"
                                else:
                                    rank_class = "rank-other"
                                
                                if lender == "Gen H":
                                    rank_class += " gen-h-cell"
                                
                                html_content += f'<td class="{rank_class}">#{rank}</td>'
                            else:
                                html_content += '<td>N/A</td>'
                        
                        html_content += """
                            </tr>
                        </tbody>
                    </table>
                </div>
"""
                
                html_content += """
            </div>
        </div>
"""
    else:
        html_content += """
        <div class="no-data">
            <h3>No data available</h3>
            <p>Run the automation to generate results</p>
        </div>
"""
    
    html_content += f"""
        <div class="refresh-controls">
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Dashboard</button>
            <button class="refresh-btn" onclick="runNewScan()">▶️ Run New Scan</button>
            <div class="timestamp">
                Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </div>
        </div>
    </div>
    
    <script>
        function runNewScan() {{
            alert('To run a new scan, execute: python3 run_standalone.py in your terminal');
        }}
        
        // Auto-refresh every 5 minutes
        setTimeout(function() {{
            location.reload();
        }}, 300000);
    </script>
</body>
</html>
"""
    return html_content

def main():
    """Generate the complete dashboard."""
    print("🚀 Generating Complete MBT Dashboard...")
    
    try:
        # Load results data
        results_file = "latest_automation_results.json"
        results_data = None
        
        if os.path.exists(results_file):
            print(f"📂 Loading results from {results_file}")
            with open(results_file, 'r') as f:
                results_data = json.load(f)
        else:
            print(f"❌ Results file {results_file} not found")
            results_data = {{"results": {{}}, "timestamp": datetime.now().isoformat()}}
        
        # Generate HTML
        html_content = create_complete_dashboard(results_data)
        
        # Save HTML file
        html_file = "mbt_dashboard_complete.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Complete dashboard generated: {html_file}")
        print(f"🌐 Full path: {os.path.abspath(html_file)}")
        
        return os.path.abspath(html_file)
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        return None

if __name__ == "__main__":
    main()