"""
Test a single credit commitment scenario to verify the implementation
"""

import asyncio
import os
from real_mbt_automation import RealMBTAutomation
from dotenv import load_dotenv

load_dotenv()

async def test_single_credit_scenario():
    """Test a single credit commitment scenario."""
    
    print("🎯 Testing credit commitment scenario...")
    print("   Case: C.Employed-Single with £30k income")
    print("   Expected credit commitments:")
    print("     - Current repayments: £300 (1% of £30k)")
    print("     - Balance on completion: £3,000 (10% of £30k)")
    
    automation = RealMBTAutomation()
    
    try:
        await automation.start_browser()
        print("✅ Browser started")
        
        # Login first
        login_success = await automation.login()
        if not login_success:
            print("❌ Login failed - check credentials")
            return
        
        print("✅ Login successful")
        
        # Test the credit commitment scenario
        result = await automation.run_single_scenario("C.Employed-Single", 30000)
        
        if result:
            print(f"\n✅ Credit scenario test completed!")
            print(f"   Case: {result['case_type']}")
            print(f"   Income: £{result['income']:,}")
            print(f"   Lenders found: {len(result['lenders_data'])}")
            print(f"   Results: {result['lenders_data']}")
        else:
            print("❌ Credit scenario test failed")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    finally:
        await automation.close()
        print("✅ Browser closed")

if __name__ == "__main__":
    # Check if MBT credentials are set
    if not os.getenv("MBT_USERNAME") or not os.getenv("MBT_PASSWORD"):
        print("❌ Please set MBT_USERNAME and MBT_PASSWORD environment variables")
        print("   You can create a .env file with:")
        print("   MBT_USERNAME=your_username")
        print("   MBT_PASSWORD=your_password")
    else:
        asyncio.run(test_single_credit_scenario())