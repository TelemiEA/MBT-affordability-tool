#!/usr/bin/env python3

import os
import sys

# Change to the correct directory
os.chdir('/Users/telemiemmanuel-aina/Documents/VibeCoding/Affordability tool')

# Delete existing database
db_file = 'mbt_affordability_history.db'
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"✅ Deleted existing database: {db_file}")

# Execute the database setup
exec(open('database_setup.py').read())

# Verify the database
import sqlite3

print("\n🔍 Verifying database creation...")

try:
    conn = sqlite3.connect('mbt_affordability_history.db')
    cursor = conn.cursor()
    
    # Check total count
    cursor.execute("SELECT COUNT(*) FROM scenarios")
    total_count = cursor.fetchone()[0]
    
    # Check breakdown
    cursor.execute("""
        SELECT applicants, employment_type, COUNT(*) 
        FROM scenarios 
        GROUP BY applicants, employment_type 
        ORDER BY applicants, employment_type
    """)
    breakdown = cursor.fetchall()
    
    print(f"Total scenarios: {total_count}")
    print("Breakdown:")
    for applicants, employment, count in breakdown:
        print(f"  {applicants.title()} {employment}: {count} scenarios")
    
    conn.close()
    
    if total_count == 32:
        print("✅ Database verification successful!")
    else:
        print(f"❌ Expected 32 scenarios, found {total_count}")
        
except Exception as e:
    print(f"❌ Error verifying database: {e}")