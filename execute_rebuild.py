#!/usr/bin/env python3

import sqlite3
import os
from datetime import datetime

def create_database():
    """Create the database and tables for historical data storage."""
    
    db_path = "mbt_affordability_history.db"
    
    # Delete existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✅ Deleted existing database: {db_path}")
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create scenarios table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id TEXT NOT NULL,
            description TEXT NOT NULL,
            case_type TEXT NOT NULL,
            income INTEGER NOT NULL,
            applicants TEXT NOT NULL,  -- 'single' or 'joint'
            employment_type TEXT NOT NULL,  -- 'employed' or 'self-employed'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(scenario_id)
        )
    ''')
    
    # Create automation_runs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS automation_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            run_date DATE NOT NULL,
            run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_scenarios INTEGER DEFAULT 0,
            successful_scenarios INTEGER DEFAULT 0,
            status TEXT DEFAULT 'running',
            UNIQUE(session_id)
        )
    ''')
    
    # Create scenario_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scenario_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            scenario_id TEXT NOT NULL,
            run_date DATE NOT NULL,
            run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            gen_h_amount INTEGER,
            average_amount INTEGER,
            gen_h_difference INTEGER,
            gen_h_rank INTEGER,
            total_lenders INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES automation_runs(session_id),
            FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id)
        )
    ''')
    
    # Create lender_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lender_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            scenario_id TEXT NOT NULL,
            run_date DATE NOT NULL,
            run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            lender_name TEXT NOT NULL,
            amount INTEGER,
            rank_position INTEGER,
            FOREIGN KEY (session_id) REFERENCES automation_runs(session_id),
            FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id)
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scenario_results_date ON scenario_results(run_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lender_results_date ON lender_results(run_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scenario_results_scenario ON scenario_results(scenario_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lender_results_lender ON lender_results(lender_name)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created: {db_path}")
    return db_path

def insert_predefined_scenarios():
    """Insert all 32 predefined scenarios into the database."""
    
    conn = sqlite3.connect("mbt_affordability_history.db")
    cursor = conn.cursor()
    
    # 32 scenarios total (8 single employed + 8 single self-employed + 8 joint employed + 8 joint self-employed)
    scenarios = [
        # Single Employed (8 scenarios: £20k, £25k, £30k, £40k, £50k, £60k, £80k, £100k)
        {"scenario_id": "single_employed_20k", "description": "Sole applicant, employed, £20k", "case_type": "E.Single", "income": 20000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_25k", "description": "Sole applicant, employed, £25k", "case_type": "E.Single", "income": 25000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_30k", "description": "Sole applicant, employed, £30k", "case_type": "E.Single", "income": 30000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_40k", "description": "Sole applicant, employed, £40k", "case_type": "E.Single", "income": 40000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_50k", "description": "Sole applicant, employed, £50k", "case_type": "E.Single", "income": 50000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_60k", "description": "Sole applicant, employed, £60k", "case_type": "E.Single", "income": 60000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_80k", "description": "Sole applicant, employed, £80k", "case_type": "E.Single", "income": 80000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_100k", "description": "Sole applicant, employed, £100k", "case_type": "E.Single", "income": 100000, "applicants": "single", "employment_type": "employed"},
        
        # Single Self-Employed (8 scenarios: £20k, £25k, £30k, £40k, £50k, £60k, £80k, £100k)
        {"scenario_id": "single_self_employed_20k", "description": "Sole applicant, self-employed, £20k", "case_type": "S.Single", "income": 20000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_25k", "description": "Sole applicant, self-employed, £25k", "case_type": "S.Single", "income": 25000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_30k", "description": "Sole applicant, self-employed, £30k", "case_type": "S.Single", "income": 30000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_40k", "description": "Sole applicant, self-employed, £40k", "case_type": "S.Single", "income": 40000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_50k", "description": "Sole applicant, self-employed, £50k", "case_type": "S.Single", "income": 50000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_60k", "description": "Sole applicant, self-employed, £60k", "case_type": "S.Single", "income": 60000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_80k", "description": "Sole applicant, self-employed, £80k", "case_type": "S.Single", "income": 80000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_100k", "description": "Sole applicant, self-employed, £100k", "case_type": "S.Single", "income": 100000, "applicants": "single", "employment_type": "self-employed"},

        # Joint Employed (8 scenarios: £40k, £50k, £60k, £80k, £100k, £120k, £160k, £200k total)
        {"scenario_id": "joint_employed_40k", "description": "Joint applicants, employed, £40k total", "case_type": "E.Joint", "income": 40000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_50k", "description": "Joint applicants, employed, £50k total", "case_type": "E.Joint", "income": 50000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_60k", "description": "Joint applicants, employed, £60k total", "case_type": "E.Joint", "income": 60000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_80k", "description": "Joint applicants, employed, £80k total", "case_type": "E.Joint", "income": 80000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_100k", "description": "Joint applicants, employed, £100k total", "case_type": "E.Joint", "income": 100000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_120k", "description": "Joint applicants, employed, £120k total", "case_type": "E.Joint", "income": 120000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_160k", "description": "Joint applicants, employed, £160k total", "case_type": "E.Joint", "income": 160000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_200k", "description": "Joint applicants, employed, £200k total", "case_type": "E.Joint", "income": 200000, "applicants": "joint", "employment_type": "employed"},

        # Joint Self-Employed (8 scenarios: £40k, £50k, £60k, £80k, £100k, £120k, £160k, £200k total)
        {"scenario_id": "joint_self_employed_40k", "description": "Joint applicants, self-employed, £40k total", "case_type": "S.Joint", "income": 40000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_50k", "description": "Joint applicants, self-employed, £50k total", "case_type": "S.Joint", "income": 50000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_60k", "description": "Joint applicants, self-employed, £60k total", "case_type": "S.Joint", "income": 60000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_80k", "description": "Joint applicants, self-employed, £80k total", "case_type": "S.Joint", "income": 80000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_100k", "description": "Joint applicants, self-employed, £100k total", "case_type": "S.Joint", "income": 100000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_120k", "description": "Joint applicants, self-employed, £120k total", "case_type": "S.Joint", "income": 120000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_160k", "description": "Joint applicants, self-employed, £160k total", "case_type": "S.Joint", "income": 160000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_200k", "description": "Joint applicants, self-employed, £200k total", "case_type": "S.Joint", "income": 200000, "applicants": "joint", "employment_type": "self-employed"}
    ]
    
    # Insert scenarios
    for scenario in scenarios:
        cursor.execute('''
            INSERT OR REPLACE INTO scenarios 
            (scenario_id, description, case_type, income, applicants, employment_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            scenario["scenario_id"],
            scenario["description"], 
            scenario["case_type"],
            scenario["income"],
            scenario["applicants"],
            scenario["employment_type"]
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Inserted {len(scenarios)} scenarios into database")

def verify_database():
    """Verify the database was created correctly."""
    
    if not os.path.exists("mbt_affordability_history.db"):
        print("❌ Database file not found!")
        return False
        
    conn = sqlite3.connect("mbt_affordability_history.db")
    cursor = conn.cursor()
    
    # Check scenarios count
    cursor.execute("SELECT COUNT(*) FROM scenarios")
    count = cursor.fetchone()[0]
    
    # Get breakdown by category
    cursor.execute("""
        SELECT 
            applicants, 
            employment_type, 
            COUNT(*) as count 
        FROM scenarios 
        GROUP BY applicants, employment_type 
        ORDER BY applicants, employment_type
    """)
    breakdown = cursor.fetchall()
    
    conn.close()
    
    print(f"\n📊 Database Verification:")
    print(f"Total scenarios: {count}")
    print(f"Expected: 32")
    print(f"Status: {'✅ CORRECT' if count == 32 else '❌ INCORRECT'}")
    
    print(f"\n📋 Breakdown by category:")
    for applicants, employment_type, category_count in breakdown:
        print(f"  {applicants.title()} {employment_type}: {category_count} scenarios")
    
    # Verify we have exactly 8 scenarios in each category
    expected_categories = [
        ('joint', 'employed'),
        ('joint', 'self-employed'),
        ('single', 'employed'),
        ('single', 'self-employed')
    ]
    
    all_correct = True
    for expected_applicants, expected_employment in expected_categories:
        found = False
        for applicants, employment_type, category_count in breakdown:
            if applicants == expected_applicants and employment_type == expected_employment:
                if category_count != 8:
                    print(f"❌ Expected 8 {expected_applicants} {expected_employment} scenarios, found {category_count}")
                    all_correct = False
                found = True
                break
        if not found:
            print(f"❌ Missing {expected_applicants} {expected_employment} scenarios")
            all_correct = False
    
    print(f"\n🎯 Overall Status: {'✅ ALL CHECKS PASSED' if all_correct and count == 32 else '❌ ISSUES FOUND'}")
    
    return all_correct and count == 32

if __name__ == "__main__":
    print("🔨 Starting database rebuild...")
    os.chdir("/Users/telemiemmanuel-aina/Documents/VibeCoding/Affordability tool")
    
    create_database()
    insert_predefined_scenarios()
    
    print("\n🔍 Verifying database...")
    success = verify_database()
    
    if success:
        print("\n🎉 Database rebuild completed successfully!")
    else:
        print("\n❌ Database rebuild completed with issues!")