#!/usr/bin/env python3
"""
Force rebuild database with ONLY the 32 scenarios we want
"""

import os
import sqlite3

def force_rebuild_database():
    """Forcefully delete and recreate database with only 32 scenarios."""
    
    db_path = "mbt_affordability_history.db"
    
    print("🚀 FORCE REBUILDING MBT DATABASE")
    print("=" * 50)
    
    # Delete existing database file
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✅ Forcefully deleted: {db_path}")
    
    # Create fresh database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🏗️  Creating fresh database structure...")
    
    # Create scenarios table
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
    
    # Create other required tables
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
    
    print("📋 Inserting ONLY the 32 scenarios you want...")
    
    # Insert ONLY the 32 scenarios we want
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
    
    # Insert the scenarios
    for scenario in scenarios:
        cursor.execute('''
            INSERT INTO scenarios 
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
    
    # Verify what we created
    cursor.execute("SELECT COUNT(*) FROM scenarios")
    total_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT applicants, employment_type, COUNT(*) 
        FROM scenarios 
        GROUP BY applicants, employment_type 
        ORDER BY applicants, employment_type
    """)
    breakdown = cursor.fetchall()
    
    conn.close()
    
    print(f"\n🔍 VERIFICATION:")
    print(f"📊 Total scenarios created: {total_count}")
    print("📋 Category breakdown:")
    for row in breakdown:
        applicants, employment_type, count = row
        print(f"  - {applicants} {employment_type}: {count} scenarios")
    
    if total_count == 32:
        print(f"\n✅ SUCCESS! Database now has exactly 32 scenarios")
        print("🎉 No more £35k, £55k, £65k scenarios!")
    else:
        print(f"\n❌ ERROR: Still have {total_count} scenarios instead of 32")
    
    return total_count == 32

if __name__ == "__main__":
    force_rebuild_database()