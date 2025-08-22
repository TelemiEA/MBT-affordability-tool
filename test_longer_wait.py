#!/usr/bin/env python3
"""
Test the longer wait times
"""

import asyncio
from real_mbt_automation import RealMBTAutomation

async def test_with_longer_wait():
    """Test a joint high income scenario with the new longer waits."""
    
    automation = RealMBTAutomation()
    
    try:
        await automation.start_browser()
        
        # Login
        login_success = await automation.login()
        if not login_success:
            print("❌ Login failed")
            return
        
        print("✅ Login successful")
        
        # Test a high income joint scenario that was failing
        print("\n🧪 Testing Joint Self-Employed £200k (should wait ~240 seconds)...")
        result = await automation.run_single_scenario("S.Joint", 200000)
        
        if result and result.get('lenders_data'):
            lenders_count = len(result['lenders_data'])
            gen_h = result['lenders_data'].get('Gen H', 0)
            
            print(f"\n🎉 SUCCESS!")
            print(f"   Lenders found: {lenders_count}")
            print(f"   Gen H: £{gen_h:,}")
            
            # Show all lenders found
            print(f"\n📊 All lenders found:")
            sorted_lenders = sorted(result['lenders_data'].items(), key=lambda x: x[1], reverse=True)
            for i, (lender, amount) in enumerate(sorted_lenders, 1):
                marker = " ⭐" if lender == "Gen H" else ""
                print(f"   {i:2d}. {lender:12s}: £{amount:,}{marker}")
            
            if lenders_count >= 15:
                print("✅ Excellent! Found 15+ lenders")
            elif lenders_count >= 12:
                print("✅ Good! Found 12+ lenders")
            else:
                print("⚠️ Still low lender count - may need even longer waits")
                
        else:
            print("❌ No results obtained")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        await automation.close()

if __name__ == "__main__":
    asyncio.run(test_with_longer_wait())