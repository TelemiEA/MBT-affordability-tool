"""
Database setup for MBT Affordability Benchmarking Tool
Creates SQLite database for historical data storage
"""

import sqlite3
import os
from datetime import datetime

def create_database():
    """Create the database and tables for historical data storage."""
    
    db_path = "mbt_affordability_history.db"
    
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
            has_credit_commitments BOOLEAN DEFAULT FALSE,  -- TRUE for credit commitment scenarios
            current_repayments INTEGER DEFAULT 0,  -- 1% of income for credit scenarios
            balance_on_completion INTEGER DEFAULT 0,  -- 10% of income for credit scenarios
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
        {"scenario_id": "joint_self_employed_200k", "description": "Joint applicants, self-employed, £200k total", "case_type": "S.Joint", "income": 200000, "applicants": "joint", "employment_type": "self-employed"},
        
        # Credit Commitment Scenarios - Single Employed (8 scenarios: £20k, £25k, £30k, £40k, £50k, £60k, £80k, £100k)
        {"scenario_id": "single_employed_20k_credit", "description": "Sole applicant, employed, £20k, with credit commitments", "case_type": "C.E-Single", "income": 20000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_25k_credit", "description": "Sole applicant, employed, £25k, with credit commitments", "case_type": "C.E-Single", "income": 25000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_30k_credit", "description": "Sole applicant, employed, £30k, with credit commitments", "case_type": "C.E-Single", "income": 30000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_40k_credit", "description": "Sole applicant, employed, £40k, with credit commitments", "case_type": "C.E-Single", "income": 40000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_50k_credit", "description": "Sole applicant, employed, £50k, with credit commitments", "case_type": "C.E-Single", "income": 50000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_60k_credit", "description": "Sole applicant, employed, £60k, with credit commitments", "case_type": "C.E-Single", "income": 60000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_80k_credit", "description": "Sole applicant, employed, £80k, with credit commitments", "case_type": "C.E-Single", "income": 80000, "applicants": "single", "employment_type": "employed"},
        {"scenario_id": "single_employed_100k_credit", "description": "Sole applicant, employed, £100k, with credit commitments", "case_type": "C.E-Single", "income": 100000, "applicants": "single", "employment_type": "employed"},
        
        # Credit Commitment Scenarios - Single Self-Employed (8 scenarios: £20k, £25k, £30k, £40k, £50k, £60k, £80k, £100k)
        {"scenario_id": "single_self_employed_20k_credit", "description": "Sole applicant, self-employed, £20k, with credit commitments", "case_type": "C.Self-Single", "income": 20000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_25k_credit", "description": "Sole applicant, self-employed, £25k, with credit commitments", "case_type": "C.Self-Single", "income": 25000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_30k_credit", "description": "Sole applicant, self-employed, £30k, with credit commitments", "case_type": "C.Self-Single", "income": 30000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_40k_credit", "description": "Sole applicant, self-employed, £40k, with credit commitments", "case_type": "C.Self-Single", "income": 40000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_50k_credit", "description": "Sole applicant, self-employed, £50k, with credit commitments", "case_type": "C.Self-Single", "income": 50000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_60k_credit", "description": "Sole applicant, self-employed, £60k, with credit commitments", "case_type": "C.Self-Single", "income": 60000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_80k_credit", "description": "Sole applicant, self-employed, £80k, with credit commitments", "case_type": "C.Self-Single", "income": 80000, "applicants": "single", "employment_type": "self-employed"},
        {"scenario_id": "single_self_employed_100k_credit", "description": "Sole applicant, self-employed, £100k, with credit commitments", "case_type": "C.Self-Single", "income": 100000, "applicants": "single", "employment_type": "self-employed"},
        
        # Credit Commitment Scenarios - Joint Employed (8 scenarios: £40k, £50k, £60k, £80k, £100k, £120k, £160k, £200k total)
        {"scenario_id": "joint_employed_40k_credit", "description": "Joint applicants, employed, £40k total, with credit commitments", "case_type": "C.E-Joint", "income": 40000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_50k_credit", "description": "Joint applicants, employed, £50k total, with credit commitments", "case_type": "C.E-Joint", "income": 50000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_60k_credit", "description": "Joint applicants, employed, £60k total, with credit commitments", "case_type": "C.E-Joint", "income": 60000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_80k_credit", "description": "Joint applicants, employed, £80k total, with credit commitments", "case_type": "C.E-Joint", "income": 80000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_100k_credit", "description": "Joint applicants, employed, £100k total, with credit commitments", "case_type": "C.E-Joint", "income": 100000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_120k_credit", "description": "Joint applicants, employed, £120k total, with credit commitments", "case_type": "C.E-Joint", "income": 120000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_160k_credit", "description": "Joint applicants, employed, £160k total, with credit commitments", "case_type": "C.E-Joint", "income": 160000, "applicants": "joint", "employment_type": "employed"},
        {"scenario_id": "joint_employed_200k_credit", "description": "Joint applicants, employed, £200k total, with credit commitments", "case_type": "C.E-Joint", "income": 200000, "applicants": "joint", "employment_type": "employed"},
        
        # Credit Commitment Scenarios - Joint Self-Employed (8 scenarios: £40k, £50k, £60k, £80k, £100k, £120k, £160k, £200k total)
        {"scenario_id": "joint_self_employed_40k_credit", "description": "Joint applicants, self-employed, £40k total, with credit commitments", "case_type": "C.Self-Joint", "income": 40000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_50k_credit", "description": "Joint applicants, self-employed, £50k total, with credit commitments", "case_type": "C.Self-Joint", "income": 50000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_60k_credit", "description": "Joint applicants, self-employed, £60k total, with credit commitments", "case_type": "C.Self-Joint", "income": 60000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_80k_credit", "description": "Joint applicants, self-employed, £80k total, with credit commitments", "case_type": "C.Self-Joint", "income": 80000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_100k_credit", "description": "Joint applicants, self-employed, £100k total, with credit commitments", "case_type": "C.Self-Joint", "income": 100000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_120k_credit", "description": "Joint applicants, self-employed, £120k total, with credit commitments", "case_type": "C.Self-Joint", "income": 120000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_160k_credit", "description": "Joint applicants, self-employed, £160k total, with credit commitments", "case_type": "C.Self-Joint", "income": 160000, "applicants": "joint", "employment_type": "self-employed"},
        {"scenario_id": "joint_self_employed_200k_credit", "description": "Joint applicants, self-employed, £200k total, with credit commitments", "case_type": "C.Self-Joint", "income": 200000, "applicants": "joint", "employment_type": "self-employed"}
    ]
    
    # Insert scenarios
    for scenario in scenarios:
        # Determine if this is a credit commitment scenario
        has_credit = "_credit" in scenario["scenario_id"]
        current_repayments = int(scenario["income"] * 0.01) if has_credit else 0
        balance_on_completion = int(scenario["income"] * 0.10) if has_credit else 0
        
        cursor.execute('''
            INSERT OR REPLACE INTO scenarios 
            (scenario_id, description, case_type, income, applicants, employment_type, 
             has_credit_commitments, current_repayments, balance_on_completion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            scenario["scenario_id"],
            scenario["description"], 
            scenario["case_type"],
            scenario["income"],
            scenario["applicants"],
            scenario["employment_type"],
            has_credit,
            current_repayments,
            balance_on_completion
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Inserted {len(scenarios)} scenarios into database")

if __name__ == "__main__":
    create_database()
    insert_predefined_scenarios()
    print("🎉 Database setup complete!")