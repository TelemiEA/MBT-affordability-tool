#!/usr/bin/env python3
"""
Standalone Affordability Tool Runner
Bypasses server issues by generating static HTML files
"""

import json
import os
from datetime import datetime
from real_mbt_automation import RealMBTAutomation

def create_html_dashboard(results_data):
    """Create a self-contained HTML dashboard."""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MBT Affordability Results</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white; 
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .results-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .result-card {{
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
        }}
        .result-card:hover {{
            border-color: #4f46e5;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
        }}
        .scenario-title {{ 
            font-weight: bold; 
            color: #1e293b;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        .lender-list {{ margin: 0; padding: 0; list-style: none; }}
        .lender-item {{ 
            padding: 8px 0; 
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .lender-item:last-child {{ border-bottom: none; }}
        .lender-name {{ font-weight: 500; color: #374151; }}
        .lender-amount {{ 
            color: #059669; 
            font-weight: bold;
            background: #ecfdf5;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .status {{ 
            text-align: center; 
            margin: 20px 0; 
            padding: 15px;
            background: #f0f9ff;
            border: 2px solid #0ea5e9;
            border-radius: 8px;
            color: #0c4a6e;
        }}
        .refresh-button {{
            background: linear-gradient(135deg, #059669, #047857);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            margin: 10px;
            transition: all 0.3s ease;
        }}
        .refresh-button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(5, 150, 105, 0.4);
        }}
        .timestamp {{
            text-align: center;
            color: #64748b;
            margin-top: 20px;
            font-size: 0.9em;
        }}
        .gen-h-highlight {{
            background: linear-gradient(135deg, #10b981, #059669) !important;
            color: white !important;
            font-weight: bold !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 MBT Affordability Results</h1>
            <p>Mortgage benchmarking data from major lenders</p>
        </div>
        
        <div class="content">
            <div class="status">
                <strong>✅ Results Generated Successfully</strong><br>
                Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
            
            <button class="refresh-button" onclick="location.reload()">🔄 Refresh Page</button>
            <button class="refresh-button" onclick="runNewScan()">▶️ Run New Scan</button>
            
            <div class="results-grid">
"""

    # Add results if available
    if results_data and 'results' in results_data:
        for scenario_id, scenario_data in results_data['results'].items():
            scenario_title = scenario_data.get('description', f'Scenario {scenario_id}')
            lender_results = scenario_data.get('lender_results', {})
            
            # Sort lenders by amount (highest first)
            sorted_lenders = sorted(lender_results.items(), key=lambda x: x[1], reverse=True)
            
            html_content += f"""
                <div class="result-card">
                    <div class="scenario-title">{scenario_title}</div>
                    <ul class="lender-list">
"""
            
            for i, (lender_name, amount) in enumerate(sorted_lenders[:8]):  # Show top 8
                if amount and amount != 'N/A':
                    try:
                        amount_formatted = f"£{int(amount):,}"
                    except:
                        amount_formatted = str(amount)
                else:
                    amount_formatted = amount
                
                # Highlight Gen H in green
                name_class = "lender-name"
                amount_class = "lender-amount"
                if "Gen H" in lender_name:
                    amount_class += " gen-h-highlight"
                    
                html_content += f"""
                        <li class="lender-item">
                            <span class="{name_class}">#{i+1} {lender_name}</span>
                            <span class="{amount_class}">{amount_formatted}</span>
                        </li>
"""
            
            # Add statistics if available
            if 'statistics' in scenario_data:
                stats = scenario_data['statistics']
                gen_h_rank = stats.get('gen_h_rank', 'N/A')
                gen_h_diff = stats.get('gen_h_difference', 0)
                if gen_h_diff > 0:
                    diff_text = f"£{int(gen_h_diff):,} above average"
                    diff_color = "color: #059669;"
                else:
                    diff_text = f"£{int(abs(gen_h_diff)):,} below average"
                    diff_color = "color: #dc2626;"
                
                html_content += f"""
                        <li class="lender-item" style="border-top: 2px solid #e2e8f0; margin-top: 8px; padding-top: 8px;">
                            <span class="lender-name">Gen H Rank: #{gen_h_rank}</span>
                            <span style="{diff_color} font-size: 0.8em;">{diff_text}</span>
                        </li>
"""
            
            html_content += """
                    </ul>
                </div>
"""
    
    else:
        html_content += """
                <div class="result-card">
                    <div class="scenario-title">No Results Available</div>
                    <p>Click "Run New Scan" to generate results.</p>
                </div>
"""

    html_content += f"""
            </div>
            
            <div class="timestamp">
                Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
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
    """Run the affordability tool and generate HTML output."""
    print("🚀 Starting Standalone MBT Affordability Tool...")
    
    try:
        # Try to load existing results first
        results_file = "latest_automation_results.json"
        results_data = None
        
        if os.path.exists(results_file):
            print(f"📂 Loading existing results from {results_file}")
            with open(results_file, 'r') as f:
                results_data = json.load(f)
        else:
            print("📊 No existing results found. Run full automation? (y/n): ", end="")
            # For now, create a sample structure
            results_data = {{"results": {{}}, "timestamp": datetime.now().isoformat()}}
        
        # Generate HTML dashboard
        html_content = create_html_dashboard(results_data)
        
        # Save HTML file
        html_file = "mbt_dashboard.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard generated: {html_file}")
        print(f"🌐 Open this file in your browser:")
        print(f"   file://{os.path.abspath(html_file)}")
        
        # Also show the path for easy copying
        full_path = os.path.abspath(html_file)
        print(f"\n📋 Full path to copy:")
        print(f"   {full_path}")
        
        return full_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    main()