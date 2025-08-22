#!/usr/bin/env python3
"""
Test the enhanced lender detection to see if we can better find Nottingham, Metro, Leeds, and Atom
"""

import asyncio
from real_mbt_automation import RealMBTAutomation

async def test_lender_detection():
    """Test a scenario to see if the enhanced lender detection finds more lenders."""
    
    automation = RealMBTAutomation()
    
    try:
        await automation.start_browser()
        
        # Login
        print("🔐 Logging in...")
        login_success = await automation.login()
        if not login_success:
            print("❌ Login failed")
            return
        
        print("✅ Login successful")
        
        # Test a scenario that should have good lender coverage
        print("\n🧪 Testing Enhanced Lender Detection on £30k Single Employed...")
        print("    Looking specifically for: Nottingham, Metro, Leeds, Atom")
        
        result = await automation.run_single_scenario("E.Single", 30000)
        
        if result and result.get('lenders_data'):
            lenders_found = result['lenders_data']
            print(f"\n📊 RESULTS - Found {len(lenders_found)} lenders:")
            
            # Check specifically for the problematic lenders
            target_lenders = ['Nottingham', 'Metro', 'Leeds', 'Atom']
            
            print("\n🎯 TARGET LENDER CHECK:")
            for target in target_lenders:
                if target in lenders_found:
                    amount = lenders_found[target]
                    print(f"   ✅ {target}: £{amount:,} - FOUND!")
                else:
                    print(f"   ❌ {target}: NOT FOUND")
            
            print(f"\n📋 ALL LENDERS FOUND:")
            sorted_lenders = sorted(lenders_found.items(), key=lambda x: x[1], reverse=True)
            for i, (lender, amount) in enumerate(sorted_lenders, 1):
                marker = " 🎯" if lender in target_lenders else ""
                print(f"   {i:2d}. {lender:15s}: £{amount:,}{marker}")
            
            # Summary
            found_count = sum(1 for target in target_lenders if target in lenders_found)
            print(f"\n🎉 SUMMARY:")
            print(f"   Target lenders found: {found_count}/4")
            print(f"   Total lenders found: {len(lenders_found)}")
            
            if found_count == 4:
                print("   ✅ All target lenders detected - enhancement working!")
            elif found_count > 2:
                print("   ✅ Most target lenders detected - good improvement!")
            else:
                print("   ⚠️ Still missing some target lenders - may need more enhancement")
                
        else:
            print("❌ No results obtained - scenario may have failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        await automation.close()

if __name__ == "__main__":
    print("🔍 TESTING ENHANCED LENDER DETECTION")
    print("=" * 60)
    print("This test will check if the enhanced lender name matching")
    print("can better detect: Nottingham, Metro, Leeds, and Atom")
    print("=" * 60)
    
    asyncio.run(test_lender_detection())