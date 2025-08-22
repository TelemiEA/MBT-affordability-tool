#!/usr/bin/env python3
"""
Check what joint scenarios are in the database
"""

import sqlite3

def check_joint_scenarios():
    """Check joint scenarios in database."""
    
    conn = sqlite3.connect("mbt_affordability_history.db")
    cursor = conn.cursor()
    
    # Get joint scenarios
    cursor.execute("""
        SELECT scenario_id, income 
        FROM scenarios 
        WHERE applicants = 'joint'
        ORDER BY employment_type, income
    """)
    joint_scenarios = cursor.fetchall()
    
    print("🔍 CURRENT JOINT SCENARIOS IN DATABASE:")
    print("=" * 50)
    
    employed_incomes = []
    self_employed_incomes = []
    
    for scenario_id, income in joint_scenarios:
        if 'employed_' in scenario_id and 'self_employed_' not in scenario_id:
            employed_incomes.append(income)
        elif 'self_employed_' in scenario_id:
            self_employed_incomes.append(income)
        print(f"  - {scenario_id}: £{income:,}")
    
    print(f"\n📊 Joint Employed Incomes: {sorted(employed_incomes)}")
    print(f"📊 Joint Self-Employed Incomes: {sorted(self_employed_incomes)}")
    
    # What they should be
    expected = [40000, 50000, 60000, 80000, 100000, 120000, 160000, 200000]
    print(f"\n✅ Expected Incomes: {expected}")
    
    # Check if correct
    employed_correct = sorted(employed_incomes) == expected
    self_employed_correct = sorted(self_employed_incomes) == expected
    
    print(f"\n📋 Joint Employed Correct: {'✅' if employed_correct else '❌'}")
    print(f"📋 Joint Self-Employed Correct: {'✅' if self_employed_correct else '❌'}")
    
    conn.close()

if __name__ == "__main__":
    check_joint_scenarios()