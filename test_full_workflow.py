"""
Test Full Workflow - Test the complete automation from income update to results
"""

import asyncio
from real_mbt_automation import RealMBTAutomation

async def test_full_workflow():
    """Test the complete workflow."""
    automation = RealMBTAutomation()
    
    try:
        print("🎯 TESTING FULL WORKFLOW")
        print("=" * 50)
        
        await automation.start_browser()
        
        # Login
        login_success = await automation.login()
        if not login_success:
            print("❌ Login failed")
            return
        
        # Run one test scenario with the new navigation
        print("\n🚀 Running E.Single scenario with £25,000 income...")
        result = await automation.run_single_scenario("E.Single", 25000)
        
        if result:
            print(f"\n🎉 SUCCESS!")
            print(f"📊 Result: {result}")
        else:
            print("❌ No result obtained")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await automation.close()

if __name__ == "__main__":
    asyncio.run(test_full_workflow())