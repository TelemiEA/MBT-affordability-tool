#!/usr/bin/env python3
"""
Direct database management script that doesn't rely on shell execution
"""

import sqlite3
import os
from datetime import datetime

def main():
    # Change to the project directory
    project_dir = "/Users/telemiemmanuel-aina/Documents/VibeCoding/Affordability tool"
    os.chdir(project_dir)
    
    db_path = "mbt_affordability_history.db"
    
    print("🔨 MBT Affordability Database Manager")
    print("=" * 50)
    
    # Step 1: Delete existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✅ Deleted existing database: {db_path}")
    else:
        print(f"ℹ️  No existing database found")
    
    # Step 2: Create new database
    print("🔧 Creating new database...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    print("📋 Creating tables...")
    
    # Scenarios table
    cursor.execute('''
        CREATE TABLE scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id TEXT NOT NULL,
            description TEXT NOT NULL,
            case_type TEXT NOT NULL,
            income INTEGER NOT NULL,
            applicants TEXT NOT NULL,
            employment_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(scenario_id)
        )
    ''')
    
    # Automation runs table
    cursor.execute('''
        CREATE TABLE automation_runs (
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
    
    # Scenario results table
    cursor.execute('''
        CREATE TABLE scenario_results (
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
    
    # Lender results table
    cursor.execute('''
        CREATE TABLE lender_results (
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
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_scenario_results_date ON scenario_results(run_date)')
    cursor.execute('CREATE INDEX idx_lender_results_date ON lender_results(run_date)')
    cursor.execute('CREATE INDEX idx_scenario_results_scenario ON scenario_results(scenario_id)')
    cursor.execute('CREATE INDEX idx_lender_results_lender ON lender_results(lender_name)')
    
    print("✅ Tables created successfully")
    
    # Step 3: Insert scenarios
    print("📝 Inserting 32 predefined scenarios...")
    
    scenarios = [
        # Single Employed - 8 scenarios
        ("single_employed_20k", "Sole applicant, employed, £20k", "E.Single", 20000, "single", "employed"),
        ("single_employed_25k", "Sole applicant, employed, £25k", "E.Single", 25000, "single", "employed"),
        ("single_employed_30k", "Sole applicant, employed, £30k", "E.Single", 30000, "single", "employed"),
        ("single_employed_40k", "Sole applicant, employed, £40k", "E.Single", 40000, "single", "employed"),
        ("single_employed_50k", "Sole applicant, employed, £50k", "E.Single", 50000, "single", "employed"),
        ("single_employed_60k", "Sole applicant, employed, £60k", "E.Single", 60000, "single", "employed"),
        ("single_employed_80k", "Sole applicant, employed, £80k", "E.Single", 80000, "single", "employed"),
        ("single_employed_100k", "Sole applicant, employed, £100k", "E.Single", 100000, "single", "employed"),
        
        # Single Self-Employed - 8 scenarios
        ("single_self_employed_20k", "Sole applicant, self-employed, £20k", "S.Single", 20000, "single", "self-employed"),
        ("single_self_employed_25k", "Sole applicant, self-employed, £25k", "S.Single", 25000, "single", "self-employed"),
        ("single_self_employed_30k", "Sole applicant, self-employed, £30k", "S.Single", 30000, "single", "self-employed"),
        ("single_self_employed_40k", "Sole applicant, self-employed, £40k", "S.Single", 40000, "single", "self-employed"),
        ("single_self_employed_50k", "Sole applicant, self-employed, £50k", "S.Single", 50000, "single", "self-employed"),
        ("single_self_employed_60k", "Sole applicant, self-employed, £60k", "S.Single", 60000, "single", "self-employed"),
        ("single_self_employed_80k", "Sole applicant, self-employed, £80k", "S.Single", 80000, "single", "self-employed"),
        ("single_self_employed_100k", "Sole applicant, self-employed, £100k", "S.Single", 100000, "single", "self-employed"),
        
        # Joint Employed - 8 scenarios
        ("joint_employed_40k", "Joint applicants, employed, £40k total", "E.Joint", 40000, "joint", "employed"),
        ("joint_employed_50k", "Joint applicants, employed, £50k total", "E.Joint", 50000, "joint", "employed"),
        ("joint_employed_60k", "Joint applicants, employed, £60k total", "E.Joint", 60000, "joint", "employed"),
        ("joint_employed_80k", "Joint applicants, employed, £80k total", "E.Joint", 80000, "joint", "employed"),
        ("joint_employed_100k", "Joint applicants, employed, £100k total", "E.Joint", 100000, "joint", "employed"),
        ("joint_employed_120k", "Joint applicants, employed, £120k total", "E.Joint", 120000, "joint", "employed"),
        ("joint_employed_160k", "Joint applicants, employed, £160k total", "E.Joint", 160000, "joint", "employed"),
        ("joint_employed_200k", "Joint applicants, employed, £200k total", "E.Joint", 200000, "joint", "employed"),
        
        # Joint Self-Employed - 8 scenarios
        ("joint_self_employed_40k", "Joint applicants, self-employed, £40k total", "S.Joint", 40000, "joint", "self-employed"),
        ("joint_self_employed_50k", "Joint applicants, self-employed, £50k total", "S.Joint", 50000, "joint", "self-employed"),
        ("joint_self_employed_60k", "Joint applicants, self-employed, £60k total", "S.Joint", 60000, "joint", "self-employed"),
        ("joint_self_employed_80k", "Joint applicants, self-employed, £80k total", "S.Joint", 80000, "joint", "self-employed"),
        ("joint_self_employed_100k", "Joint applicants, self-employed, £100k total", "S.Joint", 100000, "joint", "self-employed"),
        ("joint_self_employed_120k", "Joint applicants, self-employed, £120k total", "S.Joint", 120000, "joint", "self-employed"),
        ("joint_self_employed_160k", "Joint applicants, self-employed, £160k total", "S.Joint", 160000, "joint", "self-employed"),
        ("joint_self_employed_200k", "Joint applicants, self-employed, £200k total", "S.Joint", 200000, "joint", "self-employed")
    ]
    
    for scenario in scenarios:
        cursor.execute('''
            INSERT INTO scenarios 
            (scenario_id, description, case_type, income, applicants, employment_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', scenario)
    
    conn.commit()
    print(f"✅ Successfully inserted {len(scenarios)} scenarios")
    
    # Step 4: Verify database
    print("\n🔍 Verifying database...")
    
    # Check total count
    cursor.execute("SELECT COUNT(*) FROM scenarios")
    total_count = cursor.fetchone()[0]
    
    # Check breakdown by category
    cursor.execute("""
        SELECT applicants, employment_type, COUNT(*) 
        FROM scenarios 
        GROUP BY applicants, employment_type 
        ORDER BY applicants, employment_type
    """)
    breakdown = cursor.fetchall()
    
    # Check some sample scenarios
    cursor.execute("SELECT scenario_id, description, income FROM scenarios ORDER BY scenario_id LIMIT 5")
    samples = cursor.fetchall()
    
    conn.close()
    
    print(f"\n📊 Database Verification Results:")
    print(f"Total scenarios: {total_count}")
    print(f"Expected: 32")
    print(f"Status: {'✅ CORRECT' if total_count == 32 else '❌ INCORRECT'}")
    
    print(f"\n📋 Breakdown by category:")
    all_categories_correct = True
    for applicants, employment_type, count in breakdown:
        status = "✅" if count == 8 else "❌"
        print(f"  {status} {applicants.title()} {employment_type}: {count} scenarios")
        if count != 8:
            all_categories_correct = False
    
    print(f"\n📝 Sample scenarios:")
    for scenario_id, description, income in samples:
        print(f"  - {scenario_id}: {description} (£{income:,})")
    
    # Final status
    success = (total_count == 32 and all_categories_correct)
    
    print(f"\n{'=' * 50}")
    if success:
        print("🎉 DATABASE REBUILD COMPLETED SUCCESSFULLY!")
        print("   ✅ 32 scenarios created")
        print("   ✅ All categories have 8 scenarios each")
        print("   ✅ Database structure is correct")
    else:
        print("❌ DATABASE REBUILD COMPLETED WITH ISSUES!")
        if total_count != 32:
            print(f"   ❌ Expected 32 scenarios, found {total_count}")
        if not all_categories_correct:
            print("   ❌ Some categories don't have exactly 8 scenarios")
    
    print(f"\n📁 Database location: {os.path.abspath(db_path)}")
    
    return success

if __name__ == "__main__":
    main()