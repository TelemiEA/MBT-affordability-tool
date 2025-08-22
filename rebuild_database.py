#!/usr/bin/env python3
"""
Rebuild MBT Database with 32 Scenarios Only
"""

import os
import sqlite3
from database_setup import create_database, insert_predefined_scenarios

def rebuild_database():
    """Remove old database and create new one with 32 scenarios."""
    
    db_path = "mbt_affordability_history.db"
    
    print("🚀 Rebuilding MBT Database...")
    print("=" * 50)
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✅ Removed old database: {db_path}")
    else:
        print(f"ℹ️  No existing database found")
    
    # Create fresh database
    print("🏗️  Creating fresh database structure...")
    create_database()
    
    print("📋 Inserting 32 scenarios...")
    insert_predefined_scenarios()
    
    # Verify the database
    print("🔍 Verifying database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM scenarios")
    total_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT applicants, employment_type, COUNT(*) FROM scenarios GROUP BY applicants, employment_type ORDER BY applicants, employment_type")
    breakdown = cursor.fetchall()
    
    conn.close()
    
    print("\n📊 VERIFICATION RESULTS:")
    print(f"Total scenarios: {total_count}")
    print(f"Expected: 32")
    
    if total_count == 32:
        print("✅ Total count is CORRECT")
    else:
        print("❌ Total count is WRONG")
        
    print("\n📋 Category breakdown:")
    for row in breakdown:
        applicants, employment_type, count = row
        category = f"{applicants} {employment_type}"
        expected = 8
        status = "✅" if count == expected else "❌"
        print(f"  {status} {category}: {count} scenarios")
    
    print("\n🎉 DATABASE REBUILD COMPLETED!")
    return total_count == 32

if __name__ == "__main__":
    success = rebuild_database()
    if not success:
        print("❌ Database rebuild failed - check the output above")
        exit(1)
    print("✅ Database rebuild successful - ready for automation!")