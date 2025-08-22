#!/usr/bin/env python3
"""
Simple test to check if the basic components work without MBT automation.
"""

import asyncio
from scenario_runner import ScenarioRunner
from models import create_tables
import json

async def test_simple_scenario():
    """Test scenario runner with mock data."""
    print("Testing scenario runner...")
    
    # Create database tables
    create_tables()
    
    # Create scenario runner
    runner = ScenarioRunner()
    
    # Create a simple mock scenario result
    mock_results = {
        'session_id': 'test-session-123',
        'results': {
            'joint_vanilla_40k': {
                'scenario_id': 'joint_vanilla_40k',
                'lender_results': {
                    'Gen H': 180000,
                    'Accord': 175000,
                    'Skipton': 182000,
                    'Kensington': 170000,
                    'Precise': 165000
                },
                'statistics': {
                    'average': 174400,
                    'gen_h_amount': 180000,
                    'gen_h_difference': 5600,
                    'gen_h_rank': 2
                }
            }
        },
        'timestamp': '2025-06-19T16:30:00'
    }
    
    print("Mock results created:")
    print(json.dumps(mock_results, indent=2))
    
    return mock_results

if __name__ == "__main__":
    result = asyncio.run(test_simple_scenario())
    print("\nTest completed successfully!")