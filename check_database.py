#!/usr/bin/env python3
"""
Check what scenarios are actually in the database
"""

import sqlite3
import os

def check_database():
    """Check what scenarios are in the database."""
    
    db_path = "mbt_affordability_history.db"
    
    print("🔍 CHECKING MBT DATABASE")
    print("=" * 50)
    
    if not os.path.exists(db_path):
        print(f"❌ Database file does not exist: {db_path}")
        return
    
    print(f"✅ Database file exists: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if scenarios table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scenarios'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ Scenarios table does not exist")
            conn.close()
            return
        
        print("✅ Scenarios table exists")
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM scenarios")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total scenarios in database: {total_count}")
        
        # Get breakdown by category
        cursor.execute("""
            SELECT applicants, employment_type, COUNT(*) 
            FROM scenarios 
            GROUP BY applicants, employment_type 
            ORDER BY applicants, employment_type
        """)
        breakdown = cursor.fetchall()
        
        print("\n📋 Category breakdown:")
        for row in breakdown:
            applicants, employment_type, count = row
            print(f"  - {applicants} {employment_type}: {count} scenarios")
        
        # Show all scenarios
        cursor.execute("""
            SELECT scenario_id, description, income 
            FROM scenarios 
            ORDER BY applicants, employment_type, income
        """)
        all_scenarios = cursor.fetchall()
        
        print(f"\n📝 All {len(all_scenarios)} scenarios:")
        for scenario in all_scenarios:
            scenario_id, description, income = scenario
            print(f"  - {scenario_id}: {description} (£{income:,})")
        
        conn.close()
        
        # Check if count is correct
        if total_count == 32:
            print(f"\n✅ Database has correct number of scenarios: {total_count}")
        else:
            print(f"\n❌ Database has wrong number of scenarios: {total_count} (expected 32)")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database()