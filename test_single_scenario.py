#!/usr/bin/env python3
"""
Test individual scenarios quickly without running all 32
"""

import asyncio
import sys
from real_mbt_automation import RealMBTAutomation

# Available test scenarios
SCENARIOS = {
    # Single Employed
    "1": {"case_type": "E.Single", "income": 20000, "description": "Single employed £20k"},
    "2": {"case_type": "E.Single", "income": 30000, "description": "Single employed £30k"},
    "3": {"case_type": "E.Single", "income": 50000, "description": "Single employed £50k"},
    "4": {"case_type": "E.Single", "income": 100000, "description": "Single employed £100k"},
    
    # Single Self-Employed
    "5": {"case_type": "S.Single", "income": 20000, "description": "Single self-employed £20k"},
    "6": {"case_type": "S.Single", "income": 30000, "description": "Single self-employed £30k"},
    "7": {"case_type": "S.Single", "income": 50000, "description": "Single self-employed £50k"},
    "8": {"case_type": "S.Single", "income": 100000, "description": "Single self-employed £100k"},
    
    # Joint Employed
    "9": {"case_type": "E.Joint", "income": 40000, "description": "Joint employed £40k total (£20k each)"},
    "10": {"case_type": "E.Joint", "income": 50000, "description": "Joint employed £50k total (£25k each)"},
    "11": {"case_type": "E.Joint", "income": 100000, "description": "Joint employed £100k total (£50k each)"},
    "12": {"case_type": "E.Joint", "income": 160000, "description": "Joint employed £160k total (£80k each)"},
    
    # Joint Self-Employed (one self-employed, one employed)
    "13": {"case_type": "S.Joint", "income": 40000, "description": "Joint self-employed £40k total (£20k each)"},
    "14": {"case_type": "S.Joint", "income": 50000, "description": "Joint self-employed £50k total (£25k each)"},
    "15": {"case_type": "S.Joint", "income": 100000, "description": "Joint self-employed £100k total (£50k each)"},
    "16": {"case_type": "S.Joint", "income": 200000, "description": "Joint self-employed £200k total (£100k each)"},
}

def show_menu():
    """Show available scenarios."""
    print("\n" + "="*60)
    print("🎯 MBT SINGLE SCENARIO TESTER")
    print("="*60)
    print("\nAvailable scenarios:")
    print("\n📊 SINGLE EMPLOYED:")
    for key in ["1", "2", "3", "4"]:
        print(f"  {key}. {SCENARIOS[key]['description']}")
    
    print("\n📊 SINGLE SELF-EMPLOYED:")
    for key in ["5", "6", "7", "8"]:
        print(f"  {key}. {SCENARIOS[key]['description']}")
    
    print("\n📊 JOINT EMPLOYED:")
    for key in ["9", "10", "11", "12"]:
        print(f"  {key}. {SCENARIOS[key]['description']}")
    
    print("\n📊 JOINT SELF-EMPLOYED (Mixed):")
    for key in ["13", "14", "15", "16"]:
        print(f"  {key}. {SCENARIOS[key]['description']}")
    
    print("\n💡 Usage:")
    print("  python3 test_single_scenario.py [scenario_number]")
    print("  Example: python3 test_single_scenario.py 16")
    print("\n")

async def run_single_test(scenario_num):
    """Run a single scenario test."""
    
    if scenario_num not in SCENARIOS:
        print(f"❌ Invalid scenario number: {scenario_num}")
        show_menu()
        return
    
    scenario = SCENARIOS[scenario_num]
    
    print(f"\n🚀 Testing scenario {scenario_num}: {scenario['description']}")
    print(f"   Case Type: {scenario['case_type']}")
    print(f"   Income: £{scenario['income']:,}")
    
    automation = RealMBTAutomation()
    
    try:
        await automation.start_browser()
        
        # Login
        print("\n🔐 Logging in...")
        login_success = await automation.login()
        if not login_success:
            print("❌ Login failed")
            return
        
        print("✅ Login successful")
        
        # Run the specific scenario
        print(f"\n🎯 Running scenario: {scenario['description']}")
        result = await automation.run_single_scenario(
            scenario['case_type'], 
            scenario['income']
        )
        
        if result and result.get('lenders_data'):
            print(f"\n🎉 SUCCESS! Found {len(result['lenders_data'])} lenders:")
            
            # Show results sorted by amount
            lenders = result['lenders_data']
            sorted_lenders = sorted(lenders.items(), key=lambda x: x[1], reverse=True)
            
            for i, (lender, amount) in enumerate(sorted_lenders, 1):
                gen_h_marker = " ⭐" if lender == "Gen H" else ""
                print(f"   {i:2d}. {lender:12s}: £{amount:,}{gen_h_marker}")
            
            # Show Gen H performance
            gen_h_amount = lenders.get('Gen H', 0)
            if gen_h_amount > 0:
                amounts = list(lenders.values())
                average = sum(amounts) / len(amounts)
                difference = gen_h_amount - average
                rank = sorted(amounts, reverse=True).index(gen_h_amount) + 1
                
                print(f"\n📈 Gen H Performance:")
                print(f"   Amount: £{gen_h_amount:,}")
                print(f"   Rank: {rank} of {len(amounts)}")
                print(f"   vs Average: {'+' if difference >= 0 else ''}£{difference:,.0f}")
            
            # Save result
            filename = f"test_scenario_{scenario_num}_{scenario['case_type'].lower()}_{scenario['income']}.json"
            with open(filename, "w") as f:
                import json
                json.dump(result, f, indent=2)
            print(f"\n💾 Result saved to: {filename}")
            
        else:
            print("❌ No results obtained")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await automation.close()
        print("\n✅ Test completed")

def main():
    if len(sys.argv) != 2:
        show_menu()
        return
    
    scenario_num = sys.argv[1]
    asyncio.run(run_single_test(scenario_num))

if __name__ == "__main__":
    main()