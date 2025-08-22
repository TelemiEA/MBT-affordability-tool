"""
Scenario runner and calculation engine for affordability benchmarking.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
import statistics
from sqlalchemy.orm import Session
from models import Scenario, AffordabilityResult, RunSummary, get_db, create_tables
from mbt_automation_final import MBTAutomationFinal
import asyncio


class ScenarioRunner:
    """Handles running scenarios and calculating benchmarks."""
    
    def __init__(self):
        self.target_lenders = [
            "Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom",
            "Clydesdale", "Newcastle", "Metro", "Nottingham", "Hinckley & Rugby",
            "Leeds", "Principality", "Coventry", "Santander"
        ]
        
        # Create database tables
        create_tables()
    
    def create_sample_scenarios(self) -> List[Dict]:
        """Create sample scenarios for testing."""
        scenarios = [
            {
                'scenario_id': 'joint_vanilla_40k',
                'scenario_type': 'vanilla',
                'applicant_type': 'joint',
                'applicant1_income': 40000,
                'applicant2_income': 40000,
                'applicant1_employment': 'employed',
                'applicant2_employment': 'employed',
                'age': 30,
                'term': 35,
                'notes': 'Joint application - both employed at £40k each'
            },
            {
                'scenario_id': 'single_self_employed_40k',
                'scenario_type': 'self_employed',
                'applicant_type': 'single',
                'applicant1_income': 40000,
                'applicant2_income': None,
                'applicant1_employment': 'self_employed',
                'applicant2_employment': None,
                'age': 30,
                'term': 35,
                'notes': 'Single self-employed - £40k current, £20k previous year'
            }
        ]
        return scenarios
    
    def create_all_scenarios(self) -> List[Dict]:
        """Create all 32 scenarios as specified."""
        scenarios = []
        
        # Vanilla Joint scenarios
        joint_incomes = [20000, 25000, 30000, 40000, 60000, 80000, 100000, 150000]
        for income in joint_incomes:
            scenarios.append({
                'scenario_id': f'joint_vanilla_{income//1000}k',
                'scenario_type': 'vanilla',
                'applicant_type': 'joint',
                'applicant1_income': income,
                'applicant2_income': income,
                'applicant1_employment': 'employed',
                'applicant2_employment': 'employed',
                'age': 30,
                'term': 35,
                'notes': f'Joint employed - £{income:,} each'
            })
        
        # Vanilla Single scenarios
        single_incomes = [20000, 25000, 30000, 40000, 60000, 80000, 100000, 200000]
        for income in single_incomes:
            scenarios.append({
                'scenario_id': f'single_vanilla_{income//1000}k',
                'scenario_type': 'vanilla',
                'applicant_type': 'single',
                'applicant1_income': income,
                'applicant2_income': None,
                'applicant1_employment': 'employed',
                'applicant2_employment': None,
                'age': 30,
                'term': 35,
                'notes': f'Single employed - £{income:,}'
            })
        
        # Self-employed Joint scenarios
        for income in joint_incomes:
            scenarios.append({
                'scenario_id': f'joint_self_employed_{income//1000}k',
                'scenario_type': 'self_employed',
                'applicant_type': 'joint',
                'applicant1_income': income,
                'applicant2_income': income,
                'applicant1_employment': 'self_employed',
                'applicant2_employment': 'employed',
                'age': 30,
                'term': 35,
                'notes': f'Joint: £{income:,} self-employed + £{income:,} employed (SE prev year: £{income//2:,})'
            })
        
        # Self-employed Single scenarios
        for income in single_incomes:
            scenarios.append({
                'scenario_id': f'single_self_employed_{income//1000}k',
                'scenario_type': 'self_employed',
                'applicant_type': 'single',
                'applicant1_income': income,
                'applicant2_income': None,
                'applicant1_employment': 'self_employed',
                'applicant2_employment': None,
                'age': 30,
                'term': 35,
                'notes': f'Single self-employed - £{income:,} current, £{income//2:,} previous year'
            })
        
        return scenarios
    
    def calculate_statistics(self, results: Dict[str, float]) -> Dict[str, float]:
        """Calculate average, Gen H difference, and rank."""
        if not results:
            return {'average': 0, 'gen_h_diff': 0, 'gen_h_rank': 0, 'gen_h_amount': 0}
        
        # Remove zero values and calculate average
        valid_amounts = [amount for amount in results.values() if amount > 0]
        average = statistics.mean(valid_amounts) if valid_amounts else 0
        
        # Gen H specific calculations
        gen_h_amount = results.get('Gen H', 0)
        gen_h_diff = gen_h_amount - average
        
        # Calculate rank (1 = highest amount)
        sorted_amounts = sorted(valid_amounts, reverse=True)
        gen_h_rank = sorted_amounts.index(gen_h_amount) + 1 if gen_h_amount in sorted_amounts else len(sorted_amounts)
        
        return {
            'average': average,
            'gen_h_diff': gen_h_diff,
            'gen_h_rank': gen_h_rank,
            'gen_h_amount': gen_h_amount
        }
    
    def save_scenario_to_db(self, scenario: Dict, db: Session) -> None:
        """Save scenario to database."""
        db_scenario = Scenario(
            scenario_id=scenario['scenario_id'],
            scenario_type=scenario['scenario_type'],
            applicant_type=scenario['applicant_type'],
            applicant1_income=scenario['applicant1_income'],
            applicant2_income=scenario.get('applicant2_income'),
            applicant1_employment=scenario['applicant1_employment'],
            applicant2_employment=scenario.get('applicant2_employment'),
            age=scenario['age'],
            term=scenario['term'],
            notes=scenario['notes']
        )
        
        # Check if scenario already exists
        existing = db.query(Scenario).filter(Scenario.scenario_id == scenario['scenario_id']).first()
        if not existing:
            db.add(db_scenario)
            db.commit()
    
    def save_results_to_db(self, scenario_id: str, results: Dict[str, float], 
                          session_id: str, db: Session) -> None:
        """Save results to database."""
        for lender, amount in results.items():
            db_result = AffordabilityResult(
                scenario_id=scenario_id,
                lender_name=lender,
                max_borrowing=amount,
                session_id=session_id
            )
            db.add(db_result)
        
        db.commit()
    
    def save_summary_to_db(self, scenario_id: str, session_id: str, 
                          results: Dict[str, float], stats: Dict[str, float],
                          db: Session) -> None:
        """Save run summary to database."""
        db_summary = RunSummary(
            session_id=session_id,
            scenario_id=scenario_id,
            total_lenders=len(self.target_lenders),
            successful_extractions=len([r for r in results.values() if r > 0]),
            average_borrowing=stats['average'],
            gen_h_amount=stats['gen_h_amount'],
            gen_h_difference=stats['gen_h_diff'],
            gen_h_rank=stats['gen_h_rank']
        )
        
        db.add(db_summary)
        db.commit()
    
    async def run_sample_scenarios(self) -> Dict:
        """Run sample scenarios for testing."""
        session_id = str(uuid.uuid4())
        scenarios = self.create_sample_scenarios()
        all_results = {}
        
        # Get database session
        db = next(get_db())
        
        try:
            mbt = MBTAutomationFinal()
            await mbt.start_browser(headless=True)
            
            if not await mbt.login():
                print("Failed to login to MBT")
                return {"error": "Login failed"}
            
            for scenario in scenarios:
                print(f"Running scenario: {scenario['scenario_id']}")
                
                # Save scenario to database
                self.save_scenario_to_db(scenario, db)
                
                # Run scenario (this will include mock data for testing)
                results = await mbt.run_scenario(scenario)
                
                if results:
                    # Calculate statistics
                    stats = self.calculate_statistics(results)
                    
                    # Save to database
                    self.save_results_to_db(scenario['scenario_id'], results, session_id, db)
                    self.save_summary_to_db(scenario['scenario_id'], session_id, results, stats, db)
                    
                    # Store for return
                    all_results[scenario['scenario_id']] = {
                        'results': results,
                        'statistics': stats,
                        'scenario': scenario
                    }
                    
                    print(f"Completed {scenario['scenario_id']}: Avg £{stats['average']:,.0f}, Gen H Rank {stats['gen_h_rank']}")
                else:
                    print(f"No results for {scenario['scenario_id']}")
            
            await mbt.close()
            
        except Exception as e:
            print(f"Error running scenarios: {e}")
            return {"error": str(e)}
        finally:
            db.close()
        
        return {
            'session_id': session_id,
            'results': all_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_historical_results(self, db: Session, scenario_id: Optional[str] = None) -> List[Dict]:
        """Get historical results from database."""
        query = db.query(RunSummary)
        
        if scenario_id:
            query = query.filter(RunSummary.scenario_id == scenario_id)
        
        summaries = query.order_by(RunSummary.run_date.desc()).all()
        
        results = []
        for summary in summaries:
            results.append({
                'session_id': summary.session_id,
                'scenario_id': summary.scenario_id,
                'run_date': summary.run_date.isoformat(),
                'average_borrowing': summary.average_borrowing,
                'gen_h_amount': summary.gen_h_amount,
                'gen_h_difference': summary.gen_h_difference,
                'gen_h_rank': summary.gen_h_rank,
                'successful_extractions': summary.successful_extractions,
                'total_lenders': summary.total_lenders
            })
        
        return results
    
    def get_latest_results(self, db: Session) -> Dict:
        """Get the most recent results."""
        latest_session = db.query(RunSummary).order_by(RunSummary.run_date.desc()).first()
        
        if not latest_session:
            return {}
        
        # Get all results for this session
        summaries = db.query(RunSummary).filter(
            RunSummary.session_id == latest_session.session_id
        ).all()
        
        results = {}
        for summary in summaries:
            # Get detailed results for this scenario
            detailed_results = db.query(AffordabilityResult).filter(
                AffordabilityResult.scenario_id == summary.scenario_id,
                AffordabilityResult.session_id == summary.session_id
            ).all()
            
            lender_results = {result.lender_name: result.max_borrowing for result in detailed_results}
            
            results[summary.scenario_id] = {
                'scenario_id': summary.scenario_id,
                'run_date': summary.run_date.isoformat(),
                'lender_results': lender_results,
                'statistics': {
                    'average': summary.average_borrowing,
                    'gen_h_amount': summary.gen_h_amount,
                    'gen_h_difference': summary.gen_h_difference,
                    'gen_h_rank': summary.gen_h_rank
                }
            }
        
        return {
            'session_id': latest_session.session_id,
            'results': results,
            'timestamp': latest_session.run_date.isoformat()
        }


async def test_scenario_runner():
    """Test the scenario runner."""
    runner = ScenarioRunner()
    results = await runner.run_sample_scenarios()
    
    print("\n=== Test Results ===")
    print(f"Session ID: {results.get('session_id')}")
    
    if 'results' in results:
        for scenario_id, data in results['results'].items():
            print(f"\n{scenario_id}:")
            print(f"  Average: £{data['statistics']['average']:,.0f}")
            print(f"  Gen H: £{data['statistics']['gen_h_amount']:,.0f}")
            print(f"  Gen H Rank: {data['statistics']['gen_h_rank']}")
            print(f"  Gen H Diff: £{data['statistics']['gen_h_diff']:,.0f}")


if __name__ == "__main__":
    asyncio.run(test_scenario_runner())