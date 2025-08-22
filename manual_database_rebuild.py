#!/usr/bin/env python3
"""
Manual Database Rebuild Script - Works without shell dependencies
"""

import sqlite3
import os
from datetime import datetime

def execute_database_rebuild():
    """Execute the complete database rebuild process"""
    
    # Set working directory
    os.chdir('/Users/telemiemmanuel-aina/Documents/VibeCoding/Affordability tool')
    
    db_path = 'mbt_affordability_history.db'
    
    print("🔨 MBT Affordability Database Rebuild")
    print("=" * 60)
    
    # Step 1: Remove existing database
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"✅ Removed existing database: {db_path}")
        else:
            print("ℹ️  No existing database found")
    except Exception as e:
        print(f"❌ Error removing existing database: {e}")
        return False
    
    # Step 2: Create new database and tables
    try:
        print("\n🏗️  Creating new database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
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
        
        # Create automation_runs table
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
        
        # Create scenario_results table
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
        
        # Create lender_results table
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
        
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False
    
    # Step 3: Insert the 32 predefined scenarios
    try:
        print("\n📝 Inserting 32 predefined scenarios...")
        
        scenarios_data = [
            # Single Employed (8 scenarios)
            ('single_employed_20k', 'Sole applicant, employed, £20k', 'E.Single', 20000, 'single', 'employed'),
            ('single_employed_25k', 'Sole applicant, employed, £25k', 'E.Single', 25000, 'single', 'employed'),
            ('single_employed_30k', 'Sole applicant, employed, £30k', 'E.Single', 30000, 'single', 'employed'),
            ('single_employed_40k', 'Sole applicant, employed, £40k', 'E.Single', 40000, 'single', 'employed'),
            ('single_employed_50k', 'Sole applicant, employed, £50k', 'E.Single', 50000, 'single', 'employed'),
            ('single_employed_60k', 'Sole applicant, employed, £60k', 'E.Single', 60000, 'single', 'employed'),
            ('single_employed_80k', 'Sole applicant, employed, £80k', 'E.Single', 80000, 'single', 'employed'),
            ('single_employed_100k', 'Sole applicant, employed, £100k', 'E.Single', 100000, 'single', 'employed'),
            
            # Single Self-Employed (8 scenarios)
            ('single_self_employed_20k', 'Sole applicant, self-employed, £20k', 'S.Single', 20000, 'single', 'self-employed'),
            ('single_self_employed_25k', 'Sole applicant, self-employed, £25k', 'S.Single', 25000, 'single', 'self-employed'),
            ('single_self_employed_30k', 'Sole applicant, self-employed, £30k', 'S.Single', 30000, 'single', 'self-employed'),
            ('single_self_employed_40k', 'Sole applicant, self-employed, £40k', 'S.Single', 40000, 'single', 'self-employed'),
            ('single_self_employed_50k', 'Sole applicant, self-employed, £50k', 'S.Single', 50000, 'single', 'self-employed'),
            ('single_self_employed_60k', 'Sole applicant, self-employed, £60k', 'S.Single', 60000, 'single', 'self-employed'),
            ('single_self_employed_80k', 'Sole applicant, self-employed, £80k', 'S.Single', 80000, 'single', 'self-employed'),
            ('single_self_employed_100k', 'Sole applicant, self-employed, £100k', 'S.Single', 100000, 'single', 'self-employed'),
            
            # Joint Employed (8 scenarios)
            ('joint_employed_40k', 'Joint applicants, employed, £40k total', 'E.Joint', 40000, 'joint', 'employed'),
            ('joint_employed_50k', 'Joint applicants, employed, £50k total', 'E.Joint', 50000, 'joint', 'employed'),
            ('joint_employed_60k', 'Joint applicants, employed, £60k total', 'E.Joint', 60000, 'joint', 'employed'),
            ('joint_employed_80k', 'Joint applicants, employed, £80k total', 'E.Joint', 80000, 'joint', 'employed'),
            ('joint_employed_100k', 'Joint applicants, employed, £100k total', 'E.Joint', 100000, 'joint', 'employed'),
            ('joint_employed_120k', 'Joint applicants, employed, £120k total', 'E.Joint', 120000, 'joint', 'employed'),
            ('joint_employed_160k', 'Joint applicants, employed, £160k total', 'E.Joint', 160000, 'joint', 'employed'),
            ('joint_employed_200k', 'Joint applicants, employed, £200k total', 'E.Joint', 200000, 'joint', 'employed'),
            
            # Joint Self-Employed (8 scenarios)
            ('joint_self_employed_40k', 'Joint applicants, self-employed, £40k total', 'S.Joint', 40000, 'joint', 'self-employed'),
            ('joint_self_employed_50k', 'Joint applicants, self-employed, £50k total', 'S.Joint', 50000, 'joint', 'self-employed'),
            ('joint_self_employed_60k', 'Joint applicants, self-employed, £60k total', 'S.Joint', 60000, 'joint', 'self-employed'),
            ('joint_self_employed_80k', 'Joint applicants, self-employed, £80k total', 'S.Joint', 80000, 'joint', 'self-employed'),
            ('joint_self_employed_100k', 'Joint applicants, self-employed, £100k total', 'S.Joint', 100000, 'joint', 'self-employed'),
            ('joint_self_employed_120k', 'Joint applicants, self-employed, £120k total', 'S.Joint', 120000, 'joint', 'self-employed'),
            ('joint_self_employed_160k', 'Joint applicants, self-employed, £160k total', 'S.Joint', 160000, 'joint', 'self-employed'),
            ('joint_self_employed_200k', 'Joint applicants, self-employed, £200k total', 'S.Joint', 200000, 'joint', 'self-employed')
        ]
        
        for scenario in scenarios_data:
            cursor.execute('''
                INSERT INTO scenarios 
                (scenario_id, description, case_type, income, applicants, employment_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', scenario)
        
        conn.commit()
        print(f"✅ Successfully inserted {len(scenarios_data)} scenarios")
        
    except Exception as e:
        print(f"❌ Error inserting scenarios: {e}")
        return False
    
    # Step 4: Verification
    try:
        print("\n🔍 Verifying database integrity...")
        
        # Check total count
        cursor.execute("SELECT COUNT(*) FROM scenarios")
        total_count = cursor.fetchone()[0]
        
        # Check breakdown by category
        cursor.execute("""
            SELECT applicants, employment_type, COUNT(*) as count
            FROM scenarios 
            GROUP BY applicants, employment_type 
            ORDER BY applicants, employment_type
        """)
        breakdown = cursor.fetchall()
        
        # Get sample data for verification
        cursor.execute("""
            SELECT scenario_id, description, case_type, income, applicants, employment_type 
            FROM scenarios 
            ORDER BY case_type, income 
            LIMIT 6
        """)
        sample_data = cursor.fetchall()
        
        conn.close()
        
        # Verification report
        print(f"\n📊 VERIFICATION REPORT")
        print(f"Total scenarios: {total_count}")
        print(f"Expected: 32")
        
        if total_count == 32:
            print("✅ Scenario count is CORRECT")
        else:
            print("❌ Scenario count is INCORRECT")
            return False
        
        print(f"\n📋 Category breakdown:")
        category_status = True
        for applicants, employment_type, count in breakdown:
            status = "✅" if count == 8 else "❌"
            print(f"  {status} {applicants.title()} {employment_type}: {count} scenarios")
            if count != 8:
                category_status = False
        
        if category_status:
            print("✅ All categories have exactly 8 scenarios")
        else:
            print("❌ Some categories have incorrect scenario counts")
            return False
        
        print(f"\n📝 Sample data verification:")
        for scenario_id, description, case_type, income, applicants, employment_type in sample_data:
            print(f"  • {scenario_id}: {description} ({case_type}, £{income:,})")
        
        print(f"\n{'=' * 60}")
        print("🎉 DATABASE REBUILD COMPLETED SUCCESSFULLY!")
        print("✅ All 32 scenarios created correctly")
        print("✅ All categories have exactly 8 scenarios")
        print("✅ Database structure is valid")
        print(f"✅ Database saved to: {os.path.abspath(db_path)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

# Execute the rebuild
if __name__ == "__main__":
    success = execute_database_rebuild()
    
    if success:
        print("\n🎯 READY FOR USE!")
        print("The database has been successfully rebuilt with all 32 scenarios.")
    else:
        print("\n❌ REBUILD FAILED!")
        print("Please check the errors above and try again.")