#!/usr/bin/env python3

import sqlite3
import os

# Navigate to the correct directory
os.chdir('/Users/telemiemmanuel-aina/Documents/VibeCoding/Affordability tool')

# Verify if the database exists and what's in it
if os.path.exists('mbt_affordability_history.db'):
    print("📁 Database file exists")
    
    try:
        conn = sqlite3.connect('mbt_affordability_history.db')
        cursor = conn.cursor()
        
        # Check if scenarios table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scenarios'")
        if cursor.fetchone():
            print("✅ Scenarios table exists")
            
            # Count scenarios
            cursor.execute("SELECT COUNT(*) FROM scenarios")
            count = cursor.fetchone()[0]
            print(f"📊 Total scenarios: {count}")
            
            # Show breakdown
            cursor.execute("""
                SELECT applicants, employment_type, COUNT(*) 
                FROM scenarios 
                GROUP BY applicants, employment_type 
                ORDER BY applicants, employment_type
            """)
            breakdown = cursor.fetchall()
            
            print("📋 Breakdown:")
            for applicants, employment, count in breakdown:
                print(f"  {applicants.title()} {employment}: {count} scenarios")
                
        else:
            print("❌ Scenarios table does not exist")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        
else:
    print("❌ Database file does not exist")
    print("Need to create the database...")