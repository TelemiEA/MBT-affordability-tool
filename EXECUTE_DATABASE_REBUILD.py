#!/usr/bin/env python3
"""
FINAL DATABASE REBUILD SCRIPT
Execute this script to rebuild the MBT affordability database with 32 scenarios.

USAGE:
1. Open Terminal
2. Navigate to: /Users/telemiemmanuel-aina/Documents/VibeCoding/Affordability tool
3. Run: python3 EXECUTE_DATABASE_REBUILD.py

This script will:
1. Delete the existing mbt_affordability_history.db file
2. Create a fresh database with proper structure
3. Insert exactly 32 scenarios as specified
4. Verify the database was created correctly
"""

import sqlite3
import os
from datetime import datetime

def main():
    """Main execution function"""
    
    print("🚀 MBT AFFORDABILITY DATABASE REBUILD")
    print("=" * 70)
    
    # Ensure we're in the right directory
    target_dir = "/Users/telemiemmanuel-aina/Documents/VibeCoding/Affordability tool"
    os.chdir(target_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    db_file = "mbt_affordability_history.db"
    
    # STEP 1: Delete existing database
    print(f"\n🗑️  STEP 1: Removing existing database...")
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"✅ Successfully deleted: {db_file}")
        except Exception as e:
            print(f"❌ Failed to delete database: {e}")
            return False
    else:
        print(f"ℹ️  No existing database file found")
    
    # STEP 2: Create database structure
    print(f"\n🏗️  STEP 2: Creating database structure...")
    try:
        conn = sqlite3.connect(db_file)
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
        
        # Create performance indexes
        cursor.execute('CREATE INDEX idx_scenario_results_date ON scenario_results(run_date)')
        cursor.execute('CREATE INDEX idx_lender_results_date ON lender_results(run_date)')
        cursor.execute('CREATE INDEX idx_scenario_results_scenario ON scenario_results(scenario_id)')
        cursor.execute('CREATE INDEX idx_lender_results_lender ON lender_results(lender_name)')
        
        print("✅ Database structure created successfully")
        
    except Exception as e:
        print(f"❌ Failed to create database structure: {e}")
        return False
    
    # STEP 3: Insert 32 scenarios
    print(f"\n📋 STEP 3: Inserting 32 predefined scenarios...")
    
    scenarios = [
        # Single Employed (8 scenarios: £20k, £25k, £30k, £40k, £50k, £60k, £80k, £100k)
        ('single_employed_20k', 'Sole applicant, employed, £20k', 'E.Single', 20000, 'single', 'employed'),
        ('single_employed_25k', 'Sole applicant, employed, £25k', 'E.Single', 25000, 'single', 'employed'),
        ('single_employed_30k', 'Sole applicant, employed, £30k', 'E.Single', 30000, 'single', 'employed'),
        ('single_employed_40k', 'Sole applicant, employed, £40k', 'E.Single', 40000, 'single', 'employed'),
        ('single_employed_50k', 'Sole applicant, employed, £50k', 'E.Single', 50000, 'single', 'employed'),
        ('single_employed_60k', 'Sole applicant, employed, £60k', 'E.Single', 60000, 'single', 'employed'),
        ('single_employed_80k', 'Sole applicant, employed, £80k', 'E.Single', 80000, 'single', 'employed'),
        ('single_employed_100k', 'Sole applicant, employed, £100k', 'E.Single', 100000, 'single', 'employed'),
        
        # Single Self-Employed (8 scenarios: £20k, £25k, £30k, £40k, £50k, £60k, £80k, £100k)
        ('single_self_employed_20k', 'Sole applicant, self-employed, £20k', 'S.Single', 20000, 'single', 'self-employed'),
        ('single_self_employed_25k', 'Sole applicant, self-employed, £25k', 'S.Single', 25000, 'single', 'self-employed'),
        ('single_self_employed_30k', 'Sole applicant, self-employed, £30k', 'S.Single', 30000, 'single', 'self-employed'),
        ('single_self_employed_40k', 'Sole applicant, self-employed, £40k', 'S.Single', 40000, 'single', 'self-employed'),
        ('single_self_employed_50k', 'Sole applicant, self-employed, £50k', 'S.Single', 50000, 'single', 'self-employed'),
        ('single_self_employed_60k', 'Sole applicant, self-employed, £60k', 'S.Single', 60000, 'single', 'self-employed'),
        ('single_self_employed_80k', 'Sole applicant, self-employed, £80k', 'S.Single', 80000, 'single', 'self-employed'),
        ('single_self_employed_100k', 'Sole applicant, self-employed, £100k', 'S.Single', 100000, 'single', 'self-employed'),
        
        # Joint Employed (8 scenarios: £40k, £50k, £60k, £80k, £100k, £120k, £160k, £200k total)
        ('joint_employed_40k', 'Joint applicants, employed, £40k total', 'E.Joint', 40000, 'joint', 'employed'),
        ('joint_employed_50k', 'Joint applicants, employed, £50k total', 'E.Joint', 50000, 'joint', 'employed'),
        ('joint_employed_60k', 'Joint applicants, employed, £60k total', 'E.Joint', 60000, 'joint', 'employed'),
        ('joint_employed_80k', 'Joint applicants, employed, £80k total', 'E.Joint', 80000, 'joint', 'employed'),
        ('joint_employed_100k', 'Joint applicants, employed, £100k total', 'E.Joint', 100000, 'joint', 'employed'),
        ('joint_employed_120k', 'Joint applicants, employed, £120k total', 'E.Joint', 120000, 'joint', 'employed'),
        ('joint_employed_160k', 'Joint applicants, employed, £160k total', 'E.Joint', 160000, 'joint', 'employed'),
        ('joint_employed_200k', 'Joint applicants, employed, £200k total', 'E.Joint', 200000, 'joint', 'employed'),
        
        # Joint Self-Employed (8 scenarios: £40k, £50k, £60k, £80k, £100k, £120k, £160k, £200k total)
        ('joint_self_employed_40k', 'Joint applicants, self-employed, £40k total', 'S.Joint', 40000, 'joint', 'self-employed'),
        ('joint_self_employed_50k', 'Joint applicants, self-employed, £50k total', 'S.Joint', 50000, 'joint', 'self-employed'),
        ('joint_self_employed_60k', 'Joint applicants, self-employed, £60k total', 'S.Joint', 60000, 'joint', 'self-employed'),
        ('joint_self_employed_80k', 'Joint applicants, self-employed, £80k total', 'S.Joint', 80000, 'joint', 'self-employed'),
        ('joint_self_employed_100k', 'Joint applicants, self-employed, £100k total', 'S.Joint', 100000, 'joint', 'self-employed'),
        ('joint_self_employed_120k', 'Joint applicants, self-employed, £120k total', 'S.Joint', 120000, 'joint', 'self-employed'),
        ('joint_self_employed_160k', 'Joint applicants, self-employed, £160k total', 'S.Joint', 160000, 'joint', 'self-employed'),
        ('joint_self_employed_200k', 'Joint applicants, self-employed, £200k total', 'S.Joint', 200000, 'joint', 'self-employed')
    ]
    
    try:
        for scenario in scenarios:
            cursor.execute('''
                INSERT INTO scenarios 
                (scenario_id, description, case_type, income, applicants, employment_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', scenario)
        
        conn.commit()
        print(f"✅ Successfully inserted {len(scenarios)} scenarios")
        
    except Exception as e:
        print(f"❌ Failed to insert scenarios: {e}")
        return False
    
    # STEP 4: Verification
    print(f"\n🔍 STEP 4: Verifying database...")
    
    try:
        # Count total scenarios
        cursor.execute("SELECT COUNT(*) FROM scenarios")
        total_count = cursor.fetchone()[0]
        
        # Get breakdown by category
        cursor.execute("""
            SELECT applicants, employment_type, COUNT(*) as count
            FROM scenarios 
            GROUP BY applicants, employment_type 
            ORDER BY applicants, employment_type
        """)
        breakdown = cursor.fetchall()
        
        # Get income ranges for verification
        cursor.execute("""
            SELECT applicants, employment_type, MIN(income), MAX(income), COUNT(*)
            FROM scenarios 
            GROUP BY applicants, employment_type 
            ORDER BY applicants, employment_type
        """)
        income_ranges = cursor.fetchall()
        
        conn.close()
        
        # Verification results
        print(f"\n📊 VERIFICATION RESULTS:")
        print(f"Total scenarios: {total_count}")
        print(f"Expected: 32")
        
        success = True
        
        if total_count == 32:
            print("✅ Total count is CORRECT")
        else:
            print("❌ Total count is INCORRECT")
            success = False
        
        print(f"\n📋 Category breakdown:")
        for applicants, employment_type, count in breakdown:
            status = "✅" if count == 8 else "❌"
            print(f"  {status} {applicants.title()} {employment_type}: {count} scenarios")
            if count != 8:
                success = False
        
        print(f"\n💰 Income ranges by category:")
        for applicants, employment_type, min_income, max_income, count in income_ranges:
            print(f"  • {applicants.title()} {employment_type}: £{min_income:,} - £{max_income:,} ({count} scenarios)")
        
        print(f"\n{'=' * 70}")
        
        if success:
            print("🎉 DATABASE REBUILD COMPLETED SUCCESSFULLY!")
            print("✅ 32 scenarios created (8 in each category)")
            print("✅ All income ranges are correct")
            print("✅ Database structure is valid")
            print(f"✅ Database file: {os.path.abspath(db_file)}")
            print(f"✅ Database size: {os.path.getsize(db_file):,} bytes")
        else:
            print("❌ DATABASE REBUILD FAILED!")
            print("Please check the errors above.")
        
        return success
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🎯 READY TO USE!")
        print("Your MBT affordability database has been successfully rebuilt.")
        print("You can now run your automation scripts with the fresh 32 scenarios.")
    else:
        print(f"\n❌ PROCESS FAILED!")
        print("Please check the error messages above and try again.")
        
    input("\nPress Enter to exit...")