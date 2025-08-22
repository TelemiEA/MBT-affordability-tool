"""
Enhanced MBT Server with Historical Data Storage and Full 32 Scenarios
"""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import sqlite3
import csv
from datetime import datetime, date
import traceback
import json
from real_mbt_automation import RealMBTAutomation
from supabase_client import supabase_manager

# Create FastAPI app
app = FastAPI(
    title="MBT Affordability Benchmarking Tool - Enhanced with Historical Data",
    description="Full automation with 32 scenarios and historical trend tracking",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create templates
templates = Jinja2Templates(directory="templates")

class DatabaseManager:
    """Manages database operations for historical data."""
    
    def __init__(self, db_path="mbt_affordability_history.db"):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def save_automation_run(self, session_id, total_scenarios, successful_scenarios, status="completed"):
        """Save automation run details."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = date.today().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO automation_runs 
            (session_id, run_date, total_scenarios, successful_scenarios, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, today, total_scenarios, successful_scenarios, status))
        
        conn.commit()
        conn.close()
    
    def save_scenario_result(self, session_id, scenario_id, gen_h_amount, average_amount, 
                           gen_h_difference, gen_h_rank, total_lenders):
        """Save scenario result summary."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = date.today().isoformat()
        
        cursor.execute('''
            INSERT INTO scenario_results 
            (session_id, scenario_id, run_date, gen_h_amount, average_amount, 
             gen_h_difference, gen_h_rank, total_lenders)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, scenario_id, today, gen_h_amount, average_amount, 
              gen_h_difference, gen_h_rank, total_lenders))
        
        conn.commit()
        conn.close()
    
    def save_lender_results(self, session_id, scenario_id, lender_results):
        """Save individual lender results."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = date.today().isoformat()
        
        # Sort lenders by amount for ranking
        sorted_lenders = sorted(lender_results.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (lender_name, amount) in enumerate(sorted_lenders, 1):
            cursor.execute('''
                INSERT INTO lender_results 
                (session_id, scenario_id, run_date, lender_name, amount, rank_position)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, scenario_id, today, lender_name, amount, rank))
        
        conn.commit()
        conn.close()
    
    def get_historical_data(self, scenario_id=None, lender_name=None, days=30):
        """Get historical data for trends."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if scenario_id and lender_name:
            # Get specific lender history for a scenario
            cursor.execute('''
                SELECT run_date, amount, rank_position
                FROM lender_results 
                WHERE scenario_id = ? AND lender_name = ?
                ORDER BY run_date DESC
                LIMIT ?
            ''', (scenario_id, lender_name, days))
            
        elif scenario_id:
            # Get scenario summary history
            cursor.execute('''
                SELECT run_date, gen_h_amount, average_amount, gen_h_difference, gen_h_rank
                FROM scenario_results 
                WHERE scenario_id = ?
                ORDER BY run_date DESC
                LIMIT ?
            ''', (scenario_id, days))
            
        else:
            # Get all recent data
            cursor.execute('''
                SELECT run_date, scenario_id, gen_h_amount, average_amount, gen_h_rank
                FROM scenario_results 
                ORDER BY run_date DESC, scenario_id
                LIMIT ?
            ''', (days * 10,))
        
        results = cursor.fetchall()
        conn.close()
        return results

# Initialize database manager
db_manager = DatabaseManager()

def get_all_scenarios():
    """Get all 32 predefined scenarios from database."""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT scenario_id, description, case_type, income FROM scenarios ORDER BY income')
    scenarios = cursor.fetchall()
    conn.close()
    
    return [
        {
            "scenario_id": row[0],
            "description": row[1], 
            "case_type": row[2],
            "income": row[3]
        }
        for row in scenarios
    ]

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page with enhanced features."""
    return templates.TemplateResponse("enhanced_dashboard.html", {"request": request})

@app.get("/api/run-sample-scenarios") 
async def run_sample_scenarios():
    """Run sample scenarios for testing."""
    try:
        print("🎯 Starting REAL MBT automation...")
        
        automation = RealMBTAutomation()
        await automation.start_browser()
        
        try:
            login_success = await automation.login()
            if not login_success:
                return JSONResponse(
                    status_code=400,
                    content={"error": "MBT login failed. Please check credentials."}
                )
            
            print("✅ MBT login successful, running sample scenario...")
            
            # Single test scenario
            test_scenario = {"case_type": "E.Single", "income": 30000, "description": "Sole applicant, employed, £30k"}
            
            result = await automation.run_single_scenario(test_scenario["case_type"], test_scenario["income"])
            
            if result and result.get('lenders_data'):
                session_id = f'sample-session-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
                
                # Process result
                lender_amounts = result['lenders_data']
                gen_h_amount = lender_amounts.get('Gen H', 0)
                
                if lender_amounts:
                    amounts = list(lender_amounts.values())
                    average = sum(amounts) / len(amounts)
                    gen_h_difference = gen_h_amount - average if gen_h_amount else 0
                    sorted_amounts = sorted(amounts, reverse=True)
                    gen_h_rank = sorted_amounts.index(gen_h_amount) + 1 if gen_h_amount in sorted_amounts else 0
                else:
                    average = gen_h_difference = gen_h_rank = 0
                
                # Save to database
                db_manager.save_automation_run(session_id, 1, 1, "completed")
                db_manager.save_scenario_result(session_id, "single_employed_30k", gen_h_amount, 
                                               int(average), int(gen_h_difference), gen_h_rank, len(lender_amounts))
                db_manager.save_lender_results(session_id, "single_employed_30k", lender_amounts)
                
                final_result = {
                    'session_id': session_id,
                    'status': 'success',
                    'message': 'Sample scenario completed successfully!',
                    'results': {
                        'single_employed_30k': {
                            'scenario_id': 'single_employed_30k',
                            'description': test_scenario['description'],
                            'lender_results': lender_amounts,
                            'statistics': {
                                'average': average,
                                'gen_h_amount': gen_h_amount,
                                'gen_h_difference': gen_h_difference,
                                'gen_h_rank': gen_h_rank
                            }
                        }
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
                return JSONResponse(content=final_result)
            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "No data extracted from sample scenario"}
                )
                
        finally:
            await automation.close()
        
    except Exception as e:
        print(f"❌ Error in sample automation: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": str(e)}
        )

@app.get("/api/run-full-automation")
async def run_full_automation():
    """Run ALL 32 scenarios with historical data storage."""
    try:
        print("🚀 Starting FULL 32-scenario MBT automation...")
        
        automation = RealMBTAutomation()
        await automation.start_browser()
        
        try:
            login_success = await automation.login()
            if not login_success:
                return JSONResponse(
                    status_code=400,
                    content={"error": "MBT login failed for full automation."}
                )
            
            # Get all scenarios from database
            scenarios = get_all_scenarios()
            print(f"📊 Running {len(scenarios)} scenarios...")
            
            session_id = f'full-session-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
            results = {}
            successful_count = 0
            
            # Save initial run record
            db_manager.save_automation_run(session_id, len(scenarios), 0, "running")
            
            for i, scenario in enumerate(scenarios, 1):
                print(f"\\n📊 Scenario {i}/{len(scenarios)}: {scenario['description']}")
                
                try:
                    result = await automation.run_single_scenario(
                        scenario["case_type"], 
                        scenario["income"]
                    )
                    
                    if result and result.get('lenders_data'):
                        lender_amounts = result['lenders_data']
                        gen_h_amount = lender_amounts.get('Gen H', 0)
                        
                        if lender_amounts:
                            amounts = list(lender_amounts.values())
                            average = sum(amounts) / len(amounts)
                            gen_h_difference = gen_h_amount - average if gen_h_amount else 0
                            sorted_amounts = sorted(amounts, reverse=True)
                            gen_h_rank = sorted_amounts.index(gen_h_amount) + 1 if gen_h_amount in sorted_amounts else 0
                        else:
                            average = gen_h_difference = gen_h_rank = 0
                        
                        # Save to database
                        db_manager.save_scenario_result(
                            session_id, scenario['scenario_id'], gen_h_amount,
                            int(average), int(gen_h_difference), gen_h_rank, len(lender_amounts)
                        )
                        db_manager.save_lender_results(session_id, scenario['scenario_id'], lender_amounts)
                        
                        # Add to results
                        results[scenario['scenario_id']] = {
                            'scenario_id': scenario['scenario_id'],
                            'description': scenario['description'],
                            'lender_results': lender_amounts,
                            'statistics': {
                                'average': average,
                                'gen_h_amount': gen_h_amount,
                                'gen_h_difference': gen_h_difference,
                                'gen_h_rank': gen_h_rank
                            }
                        }
                        
                        successful_count += 1
                        print(f"✅ Scenario {i} completed: {len(lender_amounts)} lenders")
                        
                except Exception as e:
                    print(f"❌ Scenario {i} failed: {e}")
                    continue
            
            # Update run record with final counts
            db_manager.save_automation_run(session_id, len(scenarios), successful_count, "completed")
            
            final_result = {
                'session_id': session_id,
                'status': 'success',
                'message': f'Full automation completed! {successful_count}/{len(scenarios)} scenarios successful.',
                'results': results,
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_scenarios': len(scenarios),
                    'successful_scenarios': successful_count,
                    'failed_scenarios': len(scenarios) - successful_count
                }
            }
            
            # Save complete results  
            with open(f"full_automation_{session_id}.json", "w") as f:
                json.dump(final_result, f, indent=2)
            
            # Also save as latest results for easy access
            with open("latest_automation_results.json", "w") as f:
                json.dump(final_result, f, indent=2)
            
            print(f"🎉 Full automation completed: {successful_count}/{len(scenarios)} scenarios")
            return JSONResponse(content=final_result)
            
        finally:
            await automation.close()
        
    except Exception as e:
        print(f"❌ Error in full automation: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": str(e)}
        )

def calculate_summary_statistics(results):
    """Calculate summary statistics from scenario results."""
    if not results:
        return {
            'average_gen_h_rank': 0,
            'rank_percentages': {'rank_1_percent': 0, 'rank_2_percent': 0, 'rank_3_percent': 0},
            'top_3_percent': 0
        }
    
    # Extract Gen H ranks
    gen_h_ranks = []
    for scenario_data in results.values():
        stats = scenario_data.get('statistics', {})
        rank = stats.get('gen_h_rank', 0)
        if rank > 0:
            gen_h_ranks.append(rank)
    
    if not gen_h_ranks:
        return {
            'average_gen_h_rank': 0,
            'rank_percentages': {'rank_1_percent': 0, 'rank_2_percent': 0, 'rank_3_percent': 0},
            'top_3_percent': 0
        }
    
    # Calculate statistics
    avg_rank = sum(gen_h_ranks) / len(gen_h_ranks)
    rank_1_count = sum(1 for rank in gen_h_ranks if rank == 1)
    rank_2_count = sum(1 for rank in gen_h_ranks if rank == 2)
    rank_3_count = sum(1 for rank in gen_h_ranks if rank == 3)
    top_3_count = rank_1_count + rank_2_count + rank_3_count
    
    total_scenarios = len(gen_h_ranks)
    
    return {
        'average_gen_h_rank': round(avg_rank, 2),
        'rank_percentages': {
            'rank_1_percent': round((rank_1_count / total_scenarios) * 100, 1),
            'rank_2_percent': round((rank_2_count / total_scenarios) * 100, 1),
            'rank_3_percent': round((rank_3_count / total_scenarios) * 100, 1)
        },
        'top_3_percent': round((top_3_count / total_scenarios) * 100, 1)
    }

@app.get("/api/run-credit-scenarios")
async def run_credit_scenarios():
    """Run ONLY the 32 credit commitment scenarios (much faster than full 64)."""
    try:
        print("💳 Starting CREDIT COMMITMENT ONLY automation...")
        print("   This will run only the 32 scenarios with credit commitments")
        
        automation = RealMBTAutomation()
        await automation.start_browser()
        
        try:
            login_success = await automation.login()
            if not login_success:
                return JSONResponse(
                    status_code=400,
                    content={"error": "MBT login failed. Please check credentials."}
                )
            
            print("✅ MBT login successful, running CREDIT COMMITMENT scenarios...")
            
            # Get ONLY credit commitment scenarios from database
            credit_scenarios = []
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT scenario_id, description, case_type, income 
                FROM scenarios 
                WHERE has_credit_commitments = 1
                ORDER BY income
            ''')
            credit_rows = cursor.fetchall()
            conn.close()
            
            for row in credit_rows:
                credit_scenarios.append({
                    "scenario_id": row[0],
                    "description": row[1], 
                    "case_type": row[2],
                    "income": row[3]
                })
            
            print(f"📋 Found {len(credit_scenarios)} credit commitment scenarios to run")
            
            # Generate session ID for this credit run
            session_id = f'credit-session-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
            
            # Run credit scenarios
            successful_count = 0
            results = {}
            
            for i, scenario in enumerate(credit_scenarios, 1):
                try:
                    print(f"\n🎯 Running credit scenario {i}/{len(credit_scenarios)}: {scenario['scenario_id']}")
                    
                    result = await automation.run_single_scenario(scenario["case_type"], scenario["income"])
                    
                    if result and result.get('lenders_data'):
                        # Process result
                        lender_amounts = result['lenders_data']
                        gen_h_amount = lender_amounts.get('Gen H', 0)
                        
                        if lender_amounts:
                            amounts = list(lender_amounts.values())
                            average = sum(amounts) / len(amounts)
                            gen_h_difference = gen_h_amount - average if gen_h_amount else 0
                            sorted_amounts = sorted(amounts, reverse=True)
                            gen_h_rank = sorted_amounts.index(gen_h_amount) + 1 if gen_h_amount in sorted_amounts else 0
                        else:
                            average = gen_h_difference = gen_h_rank = 0
                        
                        # Save to database
                        db_manager.save_scenario_result(session_id, scenario["scenario_id"], gen_h_amount, 
                                                       int(average), int(gen_h_difference), gen_h_rank, len(lender_amounts))
                        db_manager.save_lender_results(session_id, scenario["scenario_id"], lender_amounts)
                        
                        # Add to results
                        results[scenario['scenario_id']] = {
                            'scenario_id': scenario['scenario_id'],
                            'description': scenario['description'],
                            'lender_results': lender_amounts,
                            'statistics': {
                                'average': average,
                                'gen_h_amount': gen_h_amount,
                                'gen_h_difference': gen_h_difference,
                                'gen_h_rank': gen_h_rank
                            }
                        }
                        
                        successful_count += 1
                        print(f"   ✅ Success: {len(lender_amounts)} lenders, Gen H: £{gen_h_amount:,}")
                    else:
                        print(f"   ❌ Failed: No data extracted")
                
                except Exception as scenario_error:
                    print(f"   ❌ Scenario error: {scenario_error}")
                    continue
            
            # Save automation run details
            db_manager.save_automation_run(session_id, len(credit_scenarios), successful_count, "completed")
            
            # Calculate summary statistics for final result
            summary_stats = calculate_summary_statistics(results)
            
            # Create final result
            final_result = {
                'session_id': session_id,
                'status': 'success',
                'type': 'credit_commitment_scenarios',
                'message': f'Credit commitment automation completed: {successful_count}/{len(credit_scenarios)} scenarios',
                'total_scenarios': len(credit_scenarios),
                'successful_scenarios': successful_count,
                'results': results,
                'summary_statistics': summary_stats,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to Supabase for historical tracking
            print("💾 Saving results to Supabase for historical analysis...")
            try:
                # Save automation run summary
                await supabase_manager.save_automation_run(
                    session_id=session_id,
                    run_type='credit',
                    total_scenarios=len(credit_scenarios),
                    successful_scenarios=successful_count,
                    results_data=final_result
                )
                
                # Save individual scenario results
                for scenario_id, scenario_data in results.items():
                    await supabase_manager.save_scenario_results(session_id, scenario_id, scenario_data)
                
                print("✅ Results saved to Supabase successfully")
            except Exception as supabase_error:
                print(f"⚠️ Warning: Could not save to Supabase: {supabase_error}")
                # Continue with local storage - don't fail the automation
            
            # Save complete results  
            with open(f"credit_automation_{session_id}.json", "w") as f:
                json.dump(final_result, f, indent=2)
            
            # Also save as latest credit results
            with open("latest_credit_results.json", "w") as f:
                json.dump(final_result, f, indent=2)
            
            print(f"💳 Credit automation completed: {successful_count}/{len(credit_scenarios)} scenarios")
            return JSONResponse(content=final_result)
            
        finally:
            await automation.close()
        
    except Exception as e:
        print(f"❌ Error in credit automation: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": str(e)}
        )

@app.get("/api/latest-results")
async def get_latest_results():
    """Get latest automation results with enhanced grouping and statistics."""
    try:
        print("🔍 API /api/latest-results called")
        
        # Try to load latest saved results first - check both credit and normal results
        credit_file = "latest_credit_results.json"
        normal_file = "latest_automation_results.json"
        
        # Determine which file to load (prefer the more recent one)
        results_file = None
        if os.path.exists(credit_file) and os.path.exists(normal_file):
            # Both exist, use the more recent one
            credit_time = os.path.getmtime(credit_file)
            normal_time = os.path.getmtime(normal_file)
            if credit_time > normal_time:
                results_file = credit_file
                print("📁 Loading latest_credit_results.json (more recent)")
            else:
                results_file = normal_file
                print("📁 Loading latest_automation_results.json (more recent)")
        elif os.path.exists(credit_file):
            results_file = credit_file
            print("📁 Loading latest_credit_results.json (only available)")
        elif os.path.exists(normal_file):
            results_file = normal_file
            print("📁 Loading latest_automation_results.json (only available)")
        
        if results_file:
            with open(results_file, 'r') as f:
                data = json.load(f)
            print(f"📊 Loaded {len(data.get('results', {}))} scenarios from {results_file}")
            enhanced = enhance_results_with_grouping_and_stats(data)
            print(f"🔑 Returning enhanced data with keys: {list(enhanced.keys())}")
            return enhanced
        
        # Try to load latest results file
        import glob
        result_files = glob.glob("full_automation_*.json")
        if result_files:
            latest_file = max(result_files, key=os.path.getctime)
            print(f"📁 Loading {latest_file}")
            with open(latest_file, 'r') as f:
                data = json.load(f)
            enhanced = enhance_results_with_grouping_and_stats(data)
            return enhanced
        
        # Fallback to sample results
        if os.path.exists("real_mbt_results.json"):
            print("📁 Loading real_mbt_results.json")
            with open("real_mbt_results.json", 'r') as f:
                data = json.load(f)
            enhanced = enhance_results_with_grouping_and_stats(data)
            return enhanced
        
        print("❌ No results files found")
        return {"message": "No results found. Run some scenarios first."}
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Error loading results: {e}"}

def enhance_results_with_grouping_and_stats(data):
    """Enhance results with grouping and summary statistics."""
    print(f"🔍 enhance_results_with_grouping_and_stats called with {len(data.get('results', {}))} scenarios")
    
    if not data.get('results'):
        print("❌ No results data found")
        return data
    
    # Group scenarios by type (handle both normal and credit commitment scenarios)
    grouped_results = {
        'sole_employed': {},
        'sole_self_employed': {},
        'joint_employed': {},
        'joint_self_employed': {},
        'sole_employed_credit': {},
        'sole_self_employed_credit': {},
        'joint_employed_credit': {},
        'joint_self_employed_credit': {}
    }
    
    # Helper function to extract income from scenario description
    def extract_income_amount(description):
        import re
        match = re.search(r'£(\d+)k', description)
        if match:
            return int(match.group(1)) * 1000
        return 0
    
    # Statistics tracking
    all_ranks = []
    rank_counts = {1: 0, 2: 0, 3: 0}
    total_scenarios_with_ranks = 0
    
    print("📊 Processing scenarios for grouping:")
    
    # First, collect scenarios with their income amounts
    scenarios_with_income = []
    for scenario_id, scenario_data in data['results'].items():
        # Determine scenario group based on actual scenario ID patterns (handle credit scenarios)
        if '_credit' in scenario_id:
            # Credit commitment scenarios
            if scenario_id.startswith('single_employed'):
                group = 'sole_employed_credit'
            elif scenario_id.startswith('single_self_employed'):
                group = 'sole_self_employed_credit'
            elif scenario_id.startswith('joint_employed'):
                group = 'joint_employed_credit'
            elif scenario_id.startswith('joint_self_employed'):
                group = 'joint_self_employed_credit'
            else:
                print(f"⚠️ Unknown credit scenario type: {scenario_id}")
                group = 'sole_employed_credit'  # fallback
        else:
            # Normal scenarios
            if scenario_id.startswith('single_employed'):
                group = 'sole_employed'
            elif scenario_id.startswith('single_self_employed'):
                group = 'sole_self_employed'
            elif scenario_id.startswith('joint_employed'):
                group = 'joint_employed'
            elif scenario_id.startswith('joint_self_employed'):
                group = 'joint_self_employed'
            else:
                print(f"⚠️ Unknown scenario type: {scenario_id}")
                group = 'sole_employed'  # fallback
        
        # Extract income amount for sorting
        description = scenario_data.get('description', '')
        income_amount = extract_income_amount(description)
        
        scenarios_with_income.append((scenario_id, scenario_data, group, income_amount))
        print(f"  {scenario_id} -> {group} (£{income_amount:,})")
    
    # Sort scenarios within each group by income amount
    # Define group order: sole_employed, sole_self_employed, joint_employed, joint_self_employed, then credit versions
    group_order = {
        'sole_employed': 0, 'sole_self_employed': 1, 'joint_employed': 2, 'joint_self_employed': 3,
        'sole_employed_credit': 4, 'sole_self_employed_credit': 5, 'joint_employed_credit': 6, 'joint_self_employed_credit': 7
    }
    scenarios_with_income.sort(key=lambda x: (group_order.get(x[2], 8), x[3]))  # Sort by group order, then income
    
    print(f"🔧 Sorted scenarios order:")
    for scenario_id, scenario_data, group, income_amount in scenarios_with_income:
        print(f"  {scenario_id} -> {group} (£{income_amount:,})")
    
    # Now populate grouped_results in sorted order
    for scenario_id, scenario_data, group, income_amount in scenarios_with_income:
        grouped_results[group][scenario_id] = scenario_data
        
        # Track ranking statistics
        gen_h_rank = scenario_data.get('statistics', {}).get('gen_h_rank')
        if gen_h_rank and isinstance(gen_h_rank, int) and gen_h_rank > 0:
            all_ranks.append(gen_h_rank)
            total_scenarios_with_ranks += 1
            
            if gen_h_rank in rank_counts:
                rank_counts[gen_h_rank] += 1
    
    # Calculate summary statistics
    summary_stats = {
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
    
    # Enhanced data structure
    enhanced_data = {
        **data,
        'grouped_results': grouped_results,
        'summary_statistics': summary_stats,
        'group_headers': {
            'sole_employed': '👤 Sole Employed Scenarios (£20k - £200k)',
            'sole_self_employed': '👤 Sole Self-Employed Scenarios (£20k - £200k)', 
            'joint_employed': '👥 Joint Employed Scenarios (£40k - £200k total)',
            'joint_self_employed': '👥 Joint Self-Employed Scenarios (£40k - £200k total)',
            'sole_employed_credit': '👤💳 Sole Employed with Credit Commitments (£20k - £100k)',
            'sole_self_employed_credit': '👤💳 Sole Self-Employed with Credit Commitments (£20k - £100k)',
            'joint_employed_credit': '👥💳 Joint Employed with Credit Commitments (£40k - £200k total)',
            'joint_self_employed_credit': '👥💳 Joint Self-Employed with Credit Commitments (£40k - £200k total)'
        }
    }
    
    print("✅ Grouping completed:")
    for group_key, scenarios in grouped_results.items():
        print(f"  {group_key}: {len(scenarios)} scenarios")
    
    print(f"🔑 Enhanced data keys: {list(enhanced_data.keys())}")
    return enhanced_data

@app.get("/api/analytics-data")
async def get_analytics_data():
    """Get analytics data for charts from latest results."""
    try:
        # Load latest results
        if os.path.exists("latest_automation_results.json"):
            with open("latest_automation_results.json", 'r') as f:
                data = json.load(f)
        else:
            return {"error": "No automation results available for analytics"}
        
        if not data.get('results'):
            return {"error": "No results data available"}
        
        # Prepare analytics data
        income_affordability_data = []
        employment_type_data = {}
        scenario_performance_data = {}
        
        for scenario_id, scenario_data in data['results'].items():
            # Extract income from scenario description or ID
            description = scenario_data.get('description', '')
            gen_h_amount = scenario_data.get('statistics', {}).get('gen_h_amount', 0)
            
            # Parse income from description (e.g., "Sole applicant, employed, £30k")
            import re
            income_match = re.search(r'£(\d+)k', description)
            if income_match:
                income = int(income_match.group(1)) * 1000
                
                # Income vs affordability data
                if gen_h_amount > 0:
                    income_affordability_data.append({
                        'income': income,
                        'affordability': gen_h_amount,
                        'scenario_type': 'joint' if 'joint' in description.lower() else 'sole',
                        'employment_type': 'self-employed' if 'self-employed' in description.lower() else 'employed'
                    })
            
            # Employment type analysis
            if 'sole' in description.lower() and 'employed' in description.lower():
                if 'self-employed' in description.lower():
                    employment_type_data['Sole Self-Employed'] = employment_type_data.get('Sole Self-Employed', 0) + 1
                else:
                    employment_type_data['Sole Employed'] = employment_type_data.get('Sole Employed', 0) + 1
            elif 'joint' in description.lower():
                if 'self-employed' in description.lower():
                    employment_type_data['Joint Self-Employed'] = employment_type_data.get('Joint Self-Employed', 0) + 1
                else:
                    employment_type_data['Joint Employed'] = employment_type_data.get('Joint Employed', 0) + 1
            
            # Scenario performance (Gen H rank)
            gen_h_rank = scenario_data.get('statistics', {}).get('gen_h_rank')
            if gen_h_rank:
                scenario_performance_data[scenario_id] = {
                    'description': description,
                    'rank': gen_h_rank,
                    'gen_h_amount': gen_h_amount,
                    'average_amount': scenario_data.get('statistics', {}).get('average', 0)
                }
        
        analytics_data = {
            'income_affordability': sorted(income_affordability_data, key=lambda x: x['income']),
            'employment_type_distribution': employment_type_data,
            'scenario_performance': scenario_performance_data,
            'data_timestamp': data.get('timestamp'),
            'total_scenarios_analyzed': len(data['results'])
        }
        
        return analytics_data
        
    except Exception as e:
        return {"error": f"Error generating analytics data: {e}"}

@app.get("/api/historical-data/{scenario_id}")
async def get_historical_data(scenario_id: str):
    """Get historical data for a specific scenario."""
    try:
        historical_data = db_manager.get_historical_data(scenario_id=scenario_id, days=30)
        
        return {
            "scenario_id": scenario_id,
            "historical_data": [
                {
                    "date": row[0],
                    "gen_h_amount": row[1],
                    "average_amount": row[2], 
                    "gen_h_difference": row[3],
                    "gen_h_rank": row[4]
                }
                for row in historical_data
            ]
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting historical data: {e}"}
        )

@app.get("/api/lender-trends/{lender_name}")
async def get_lender_trends(lender_name: str):
    """Get trends for a specific lender across all scenarios."""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT lr.run_date, lr.scenario_id, lr.amount, lr.rank_position, s.description
            FROM lender_results lr
            JOIN scenarios s ON lr.scenario_id = s.scenario_id
            WHERE lr.lender_name = ?
            ORDER BY lr.run_date DESC, s.income
            LIMIT 100
        ''', (lender_name,))
        
        results = cursor.fetchall()
        conn.close()
        
        return {
            "lender_name": lender_name,
            "trends": [
                {
                    "date": row[0],
                    "scenario_id": row[1],
                    "scenario_description": row[4],
                    "amount": row[2],
                    "rank": row[3]
                }
                for row in results
            ]
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting lender trends: {e}"}
        )

def simple_csv_export(data, filename):
    """Simple CSV export without pandas dependency."""
    try:
        results = data.get('results', {})
        if not results:
            return None
        
        # Collect all unique lender names
        all_lenders = set()
        for scenario_data in results.values():
            lenders = scenario_data.get('lender_results', {})
            all_lenders.update(lenders.keys())
        
        all_lenders = sorted(list(all_lenders))
        
        # Create CSV
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
                
                row = {
                    'scenario_id': scenario_id,
                    'description': scenario_data.get('description', ''),
                    'employment_type': get_employment_type_simple(scenario_id),
                    'applicant_type': get_applicant_type_simple(scenario_id),
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
        
        return filename
        
    except Exception as e:
        print(f"CSV export error: {e}")
        return None

def simple_json_export(data, filename):
    """Simple JSON export."""
    try:
        export_data = {
            'export_info': {
                'export_date': datetime.now().isoformat(),
                'total_scenarios': len(data.get('results', {})),
                'format_version': '1.0'
            },
            **data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        return filename
        
    except Exception as e:
        print(f"JSON export error: {e}")
        return None

def get_employment_type_simple(scenario_id):
    """Get employment type from scenario ID."""
    if 'employed' in scenario_id and 'self' not in scenario_id:
        return 'Employed'
    elif 'self_employed' in scenario_id:
        return 'Self-Employed'
    else:
        return 'Mixed'

def get_applicant_type_simple(scenario_id):
    """Get applicant type from scenario ID."""
    if scenario_id.startswith('single_'):
        return 'Single'
    elif scenario_id.startswith('joint_'):
        return 'Joint'
    else:
        return 'Unknown'

@app.get("/api/export-data/{format_type}")
async def export_data(format_type: str):
    """Export data in specified format - FIXED VERSION."""
    print(f"🔍 Export request received for format: {format_type}")
    try:
        # Determine which results file to export (credit vs normal scenarios)
        credit_file = "latest_credit_results.json"
        normal_file = "latest_automation_results.json"
        
        # Check which file exists and is more recent
        results_file = None
        if os.path.exists(credit_file) and os.path.exists(normal_file):
            # Both exist, use the more recent one
            credit_time = os.path.getmtime(credit_file)
            normal_time = os.path.getmtime(normal_file)
            if credit_time > normal_time:
                results_file = credit_file
                print("📁 Using credit results (more recent)")
            else:
                results_file = normal_file
                print("📁 Using normal results (more recent)")
        elif os.path.exists(credit_file):
            results_file = credit_file
            print("📁 Using credit results (only available)")
        elif os.path.exists(normal_file):
            results_file = normal_file
            print("📁 Using normal results (only available)")
        else:
            print("❌ No results file found")
            return JSONResponse(
                status_code=404,
                content={"error": "No results found. Run automation first."}
            )
        
        print(f"✅ Loading results file: {results_file}")
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results = data.get('results', {})
        
        print(f"✅ Found {len(results)} scenarios to export")
        
        if not results:
            print("❌ No scenario data found")
            return JSONResponse(
                status_code=404,
                content={"error": "No scenario results found in data."}
            )
        
        # Simplified export logic that definitely works
        if format_type.lower() == 'csv':
            print("📄 Creating CSV export...")
            filename = f"mbt_export_{timestamp}.csv"
            
            # Get all lenders
            all_lenders = set()
            for scenario_data in results.values():
                lenders = scenario_data.get('lender_results', {})
                all_lenders.update(lenders.keys())
            all_lenders = sorted(list(all_lenders))
            
            print(f"✅ Found {len(all_lenders)} unique lenders")
            
            # Write CSV
            print("📝 Writing CSV file...")
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    header = ['Scenario_ID', 'Description', 'Gen_H_Amount', 'Market_Average', 'Gen_H_Rank', 'Total_Lenders']
                    header.extend(all_lenders)
                    writer.writerow(header)
                    print(f"✅ Header written with {len(header)} columns")
                    
                    # Data
                    rows_written = 0
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
                        rows_written += 1
                    
                    print(f"✅ CSV written: {rows_written} rows")
            except Exception as e:
                print(f"❌ CSV write error: {e}")
                raise
            
        elif format_type.lower() == 'json':
            filename = f"mbt_export_{timestamp}.json"
            
            export_data = {
                'export_info': {
                    'export_date': datetime.now().isoformat(),
                    'total_scenarios': len(results),
                    'format': 'json'
                },
                'data': data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
                
        elif format_type.lower() == 'excel':
            # For now, fallback to CSV for Excel requests
            filename = f"mbt_export_{timestamp}.csv"
            
            all_lenders = set()
            for scenario_data in results.values():
                lenders = scenario_data.get('lender_results', {})
                all_lenders.update(lenders.keys())
            all_lenders = sorted(list(all_lenders))
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                header = ['Scenario_ID', 'Description', 'Gen_H_Amount', 'Market_Average', 'Gen_H_Rank', 'Total_Lenders']
                header.extend(all_lenders)
                writer.writerow(header)
                
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
                    
                    for lender in all_lenders:
                        row.append(lenders.get(lender, 0))
                    
                    writer.writerow(row)
            
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid format. Use csv, excel, or json"}
            )
        
        # Check if file was created successfully
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            return {
                "success": True, 
                "filename": filename, 
                "message": f"Data exported to {filename} ({file_size} bytes)",
                "scenarios_exported": len(results)
            }
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Export file was not created"}
            )
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Export error: {error_details}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Export error: {str(e)}"}
        )

@app.get("/api/historical-summary")
async def get_historical_summary():
    """Get historical summary statistics from Supabase."""
    try:
        summary = supabase_manager.get_historical_summary()
        return JSONResponse(content=summary)
    except Exception as e:
        print(f"❌ Error getting historical summary: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get historical summary: {str(e)}"}
        )

@app.get("/api/historical-gen-h-rank")
async def get_gen_h_rank_over_time():
    """Get Gen H rank over time for charting."""
    try:
        data = supabase_manager.get_gen_h_rank_over_time(limit=20)
        return JSONResponse(content={"data": data})
    except Exception as e:
        print(f"❌ Error getting Gen H rank over time: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get Gen H rank data: {str(e)}"}
        )

@app.get("/api/historical-gen-h-gap")
async def get_gen_h_gap_over_time():
    """Get Gen H vs average lender gap over time."""
    try:
        data = supabase_manager.get_gen_h_vs_average_gap_over_time(limit=20)
        return JSONResponse(content={"data": data})
    except Exception as e:
        print(f"❌ Error getting Gen H gap over time: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get Gen H gap data: {str(e)}"}
        )

@app.get("/api/scenario-rank-changes")
async def get_scenario_rank_changes():
    """Get rank changes for each scenario type between last two runs."""
    try:
        changes = supabase_manager.get_scenario_rank_changes()
        return JSONResponse(content=changes)
    except Exception as e:
        print(f"❌ Error getting scenario rank changes: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get rank changes: {str(e)}"}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (Railway sets this automatically)
    port = int(os.environ.get("PORT", 8001))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("🚀 Starting Enhanced MBT Affordability Benchmarking Tool...")
    print(f"📱 Dashboard will be available at: http://{host}:{port}")
    print("🗄️ Database: SQLite with historical data storage")
    print("📊 Features: 32 scenarios, trends, historical tracking")
    
    uvicorn.run(app, host=host, port=port)