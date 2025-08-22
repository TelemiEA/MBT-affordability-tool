"""
Supabase client for MBT Affordability Tool
Handles database operations for historical data storage and analytics
"""

import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseManager:
    """Manages Supabase database operations for historical MBT data."""
    
    def __init__(self):
        """Initialize Supabase client with environment variables."""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            print("⚠️ Warning: Supabase credentials not found in environment variables")
            print("   Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file")
            self.client = None
        else:
            self.client: Client = create_client(self.url, self.key)
            print("✅ Supabase client initialized successfully")
    
    def is_connected(self) -> bool:
        """Check if Supabase client is properly initialized."""
        return self.client is not None
    
    async def save_automation_run(self, session_id: str, run_type: str, total_scenarios: int, 
                                 successful_scenarios: int, results_data: Dict) -> bool:
        """Save automation run summary to database."""
        if not self.is_connected():
            print("❌ Supabase not connected - cannot save automation run")
            return False
        
        try:
            # Extract summary statistics from results
            summary_stats = results_data.get('summary_statistics', {})
            
            run_data = {
                'session_id': session_id,
                'run_type': run_type,  # 'normal', 'credit', 'full'
                'total_scenarios': total_scenarios,
                'successful_scenarios': successful_scenarios,
                'average_gen_h_rank': summary_stats.get('average_gen_h_rank', 0),
                'rank_1_percentage': summary_stats.get('rank_percentages', {}).get('rank_1_percent', 0),
                'rank_2_percentage': summary_stats.get('rank_percentages', {}).get('rank_2_percent', 0),
                'rank_3_percentage': summary_stats.get('rank_percentages', {}).get('rank_3_percent', 0),
                'top_3_percentage': summary_stats.get('top_3_percent', 0),
                'run_timestamp': datetime.now(timezone.utc).isoformat(),
                'results_json': json.dumps(results_data)
            }
            
            result = self.client.table('automation_runs').insert(run_data).execute()
            print(f"✅ Saved automation run {session_id} to Supabase")
            return True
            
        except Exception as e:
            print(f"❌ Error saving automation run to Supabase: {e}")
            return False
    
    async def save_scenario_results(self, session_id: str, scenario_id: str, scenario_data: Dict) -> bool:
        """Save individual scenario results to database."""
        if not self.is_connected():
            return False
        
        try:
            # Extract scenario details
            stats = scenario_data.get('statistics', {})
            lender_results = scenario_data.get('lender_results', {})
            
            # Calculate Gen H vs average gap
            gen_h_amount = stats.get('gen_h_amount', 0)
            average_amount = stats.get('average', 0)
            gen_h_gap = gen_h_amount - average_amount if gen_h_amount and average_amount else 0
            
            scenario_record = {
                'session_id': session_id,
                'scenario_id': scenario_id,
                'description': scenario_data.get('description', ''),
                'gen_h_amount': gen_h_amount,
                'average_lender_amount': average_amount,
                'gen_h_rank': stats.get('gen_h_rank', 0),
                'gen_h_difference': stats.get('gen_h_difference', 0),
                'gen_h_vs_average_gap': gen_h_gap,
                'total_lenders': len(lender_results),
                'lender_results_json': json.dumps(lender_results),
                'run_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            result = self.client.table('scenario_results').insert(scenario_record).execute()
            return True
            
        except Exception as e:
            print(f"❌ Error saving scenario {scenario_id} to Supabase: {e}")
            return False
    
    def get_historical_summary(self) -> Dict:
        """Get historical summary statistics from database."""
        if not self.is_connected():
            return {'error': 'Database not connected'}
        
        try:
            # Get total automation runs
            runs_result = self.client.table('automation_runs').select('*').execute()
            total_runs = len(runs_result.data)
            
            if total_runs == 0:
                return {
                    'total_runs': 0,
                    'average_gen_h_rank': 0,
                    'best_performing_scenario': 'No data',
                    'last_run': 'No runs yet'
                }
            
            # Get latest run
            latest_run = self.client.table('automation_runs')\
                .select('*')\
                .order('run_timestamp', desc=True)\
                .limit(1).execute()
            
            # Calculate average Gen H rank across all runs
            avg_rank_result = self.client.rpc('calculate_average_gen_h_rank').execute()
            avg_gen_h_rank = avg_rank_result.data if avg_rank_result.data else 0
            
            # Get best performing scenario (highest average Gen H rank)
            best_scenario_result = self.client.rpc('get_best_performing_scenario').execute()
            best_scenario = best_scenario_result.data if best_scenario_result.data else 'No data'
            
            return {
                'total_runs': total_runs,
                'average_gen_h_rank': round(avg_gen_h_rank, 2),
                'best_performing_scenario': best_scenario,
                'last_run': latest_run.data[0]['run_timestamp'] if latest_run.data else 'No runs'
            }
            
        except Exception as e:
            print(f"❌ Error getting historical summary: {e}")
            return {'error': str(e)}
    
    def get_gen_h_rank_over_time(self, limit: int = 20) -> List[Dict]:
        """Get Gen H rank over time for charting."""
        if not self.is_connected():
            return []
        
        try:
            result = self.client.table('automation_runs')\
                .select('run_timestamp, average_gen_h_rank, run_type')\
                .order('run_timestamp', desc=False)\
                .limit(limit).execute()
            
            return result.data
            
        except Exception as e:
            print(f"❌ Error getting Gen H rank over time: {e}")
            return []
    
    def get_gen_h_vs_average_gap_over_time(self, limit: int = 20) -> List[Dict]:
        """Get Gen H vs average lender gap over time."""
        if not self.is_connected():
            return []
        
        try:
            # This will use a custom SQL function to calculate the average gap per run
            result = self.client.rpc('get_gen_h_gap_over_time', {'run_limit': limit}).execute()
            return result.data
            
        except Exception as e:
            print(f"❌ Error getting Gen H gap over time: {e}")
            return []
    
    def get_scenario_rank_changes(self) -> Dict:
        """Get rank changes for each scenario type between the last two runs."""
        if not self.is_connected():
            return {}
        
        try:
            # Get the last two automation runs
            recent_runs = self.client.table('automation_runs')\
                .select('session_id, run_timestamp')\
                .order('run_timestamp', desc=True)\
                .limit(2).execute()
            
            if len(recent_runs.data) < 2:
                return {'error': 'Need at least 2 runs to calculate rank changes'}
            
            latest_session = recent_runs.data[0]['session_id']
            previous_session = recent_runs.data[1]['session_id']
            
            # Get scenario results for both runs
            latest_results = self.client.table('scenario_results')\
                .select('scenario_id, gen_h_rank')\
                .eq('session_id', latest_session).execute()
            
            previous_results = self.client.table('scenario_results')\
                .select('scenario_id, gen_h_rank')\
                .eq('session_id', previous_session).execute()
            
            # Calculate rank changes
            rank_changes = {}
            
            # Create lookup for previous ranks
            previous_ranks = {result['scenario_id']: result['gen_h_rank'] 
                            for result in previous_results.data}
            
            # Calculate changes
            for result in latest_results.data:
                scenario_id = result['scenario_id']
                current_rank = result['gen_h_rank']
                previous_rank = previous_ranks.get(scenario_id, current_rank)
                
                # Rank change (positive = improved rank = lower number)
                rank_change = previous_rank - current_rank
                
                # Determine scenario group
                if 'single_employed' in scenario_id and '_credit' not in scenario_id:
                    group = 'sole_employed'
                elif 'single_self_employed' in scenario_id and '_credit' not in scenario_id:
                    group = 'sole_self_employed'
                elif 'joint_employed' in scenario_id and '_credit' not in scenario_id:
                    group = 'joint_employed'
                elif 'joint_self_employed' in scenario_id and '_credit' not in scenario_id:
                    group = 'joint_self_employed'
                elif 'single_employed' in scenario_id and '_credit' in scenario_id:
                    group = 'sole_employed_credit'
                elif 'single_self_employed' in scenario_id and '_credit' in scenario_id:
                    group = 'sole_self_employed_credit'
                elif 'joint_employed' in scenario_id and '_credit' in scenario_id:
                    group = 'joint_employed_credit'
                elif 'joint_self_employed' in scenario_id and '_credit' in scenario_id:
                    group = 'joint_self_employed_credit'
                else:
                    continue
                
                if group not in rank_changes:
                    rank_changes[group] = []
                
                rank_changes[group].append({
                    'scenario_id': scenario_id,
                    'current_rank': current_rank,
                    'previous_rank': previous_rank,
                    'rank_change': rank_change
                })
            
            # Calculate average rank change per group
            group_averages = {}
            for group, scenarios in rank_changes.items():
                if scenarios:
                    avg_change = sum(s['rank_change'] for s in scenarios) / len(scenarios)
                    group_averages[group] = round(avg_change, 1)
            
            return group_averages
            
        except Exception as e:
            print(f"❌ Error getting scenario rank changes: {e}")
            return {'error': str(e)}

# Global instance
supabase_manager = SupabaseManager()