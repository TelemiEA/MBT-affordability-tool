"""
Rebuild database with credit commitment scenarios
This will add 32 new scenarios with credit commitments (total 64 scenarios)
"""

import os
import sqlite3
from database_setup import create_database, insert_predefined_scenarios

def rebuild_database_with_credit_scenarios():
    """Rebuild the database with all scenarios including credit commitment ones."""
    
    db_path = "mbt_affordability_history.db"
    
    print("🗑️  Removing old database...")
    if os.path.exists(db_path):
        os.remove(db_path)
        print("   ✅ Old database removed")
    
    print("\n🏗️  Creating new database structure...")
    create_database()
    
    print("\n📋 Inserting all scenarios (original + credit commitment scenarios)...")
    insert_predefined_scenarios()
    
    # Verify the scenarios
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count total scenarios
    cursor.execute('SELECT COUNT(*) FROM scenarios')
    total_count = cursor.fetchone()[0]
    
    # Count credit scenarios
    cursor.execute('SELECT COUNT(*) FROM scenarios WHERE has_credit_commitments = 1')
    credit_count = cursor.fetchone()[0]
    
    # Count non-credit scenarios
    cursor.execute('SELECT COUNT(*) FROM scenarios WHERE has_credit_commitments = 0')
    normal_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n📊 Database rebuild complete:")
    print(f"   ✅ Total scenarios: {total_count}")
    print(f"   ✅ Normal scenarios: {normal_count}")
    print(f"   ✅ Credit commitment scenarios: {credit_count}")
    
    if total_count == 64 and credit_count == 32 and normal_count == 32:
        print(f"\n🎉 SUCCESS! Database now has 64 scenarios (32 normal + 32 credit commitment)")
        print("   Ready to run credit commitment automation!")
        return True
    else:
        print(f"\n❌ ERROR: Expected 64 total scenarios (32 normal + 32 credit), got {total_count}")
        return False

if __name__ == "__main__":
    success = rebuild_database_with_credit_scenarios()
    if success:
        print("\n🚀 You can now test the credit commitment scenarios!")
    else:
        print("\n⚠️  Please check the database setup.")