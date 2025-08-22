#!/usr/bin/env python3
"""
Test a single credit commitment scenario
"""
import asyncio
from real_mbt_automation import RealMBTAutomation

async def test_single_scenario():
    """Test a single credit commitment scenario."""
    automation = RealMBTAutomation()
    
    try:
        # Start browser and login
        await automation.start_browser()
        login_success = await automation.login()
        
        if not login_success:
            print("❌ LOGIN FAILED")
            return
            
        # Test: Self-employed single with £30k income (C.Self-Single -> QX002304287)
        print("🧪 Testing: Self-employed single, £30k, with credit commitments")
        print(f"   Case type: C.Self-Single")
        print(f"   Expected QX: QX002304287")
        print(f"   Income: £30,000")
        print(f"   Expected credit commitments: £300 current (1%), £3,000 balance (10%)")
        
        result = await automation.run_single_scenario("C.Self-Single", 30000)
        
        if result and result.get('lenders_data'):
            print("✅ SUCCESS! Credit scenario completed successfully")
            print(f"📊 Results: {len(result['lenders_data'])} lenders returned data")
            
            # Show first few lender results
            for i, (lender, amount) in enumerate(list(result['lenders_data'].items())[:5]):
                print(f"   {lender}: £{amount:,}")
                
        else:
            print("❌ FAILED: No results returned")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        
    finally:
        await automation.close()

if __name__ == "__main__":
    asyncio.run(test_single_scenario())