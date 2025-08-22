"""
Verify that credit commitment scenarios are properly set up in database
"""

import sqlite3

def verify_credit_scenarios():
    """Verify credit commitment scenarios in database."""
    
    print("🔍 Verifying Credit Commitment Database Setup")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("mbt_affordability_history.db")
        cursor = conn.cursor()
        
        # Count total scenarios
        cursor.execute('SELECT COUNT(*) FROM scenarios')
        total_count = cursor.fetchone()[0]
        
        # Count credit scenarios
        cursor.execute('SELECT COUNT(*) FROM scenarios WHERE has_credit_commitments = 1')
        credit_count = cursor.fetchone()[0]
        
        # Count normal scenarios
        cursor.execute('SELECT COUNT(*) FROM scenarios WHERE has_credit_commitments = 0')
        normal_count = cursor.fetchone()[0]
        
        print(f"📊 Database Statistics:")
        print(f"   Total scenarios: {total_count}")
        print(f"   Normal scenarios: {normal_count}")
        print(f"   Credit scenarios: {credit_count}")
        
        if total_count == 64 and credit_count == 32 and normal_count == 32:
            print("✅ Database setup is correct!")
        else:
            print(f"❌ Database setup issue - expected 64 total (32 normal + 32 credit)")
            return False
        
        # Show sample credit scenarios
        print(f"\n📋 Sample Credit Commitment Scenarios:")
        cursor.execute('''
            SELECT scenario_id, description, income, current_repayments, balance_on_completion, case_type
            FROM scenarios 
            WHERE has_credit_commitments = 1 
            ORDER BY income 
            LIMIT 8
        ''')
        
        credit_scenarios = cursor.fetchall()
        for scenario in credit_scenarios:
            scenario_id, description, income, current_repayments, balance_on_completion, case_type = scenario
            print(f"   • {scenario_id}")
            print(f"     Income: £{income:,} | Current repayments: £{current_repayments} | Balance: £{balance_on_completion}")
            print(f"     Case: {case_type} | Description: {description}")
            print()
        
        # Test case type mapping
        print(f"📋 Credit Case Types Found:")
        cursor.execute('''
            SELECT DISTINCT case_type 
            FROM scenarios 
            WHERE has_credit_commitments = 1 
            ORDER BY case_type
        ''')
        
        case_types = cursor.fetchall()
        for case_type in case_types:
            cursor.execute('SELECT COUNT(*) FROM scenarios WHERE case_type = ?', case_type)
            count = cursor.fetchone()[0]
            print(f"   • {case_type[0]}: {count} scenarios")
        
        conn.close()
        
        print(f"\n🎯 Ready to test credit commitment automation!")
        return True
        
    except Exception as e:
        print(f"❌ Database verification error: {e}")
        return False

if __name__ == "__main__":
    verify_credit_scenarios()