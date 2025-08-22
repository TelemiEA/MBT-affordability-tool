"""
Quick test of a single credit commitment scenario
"""

import asyncio
import os
from real_mbt_automation import RealMBTAutomation
from dotenv import load_dotenv

load_dotenv()

async def quick_credit_test():
    """Quick test of credit commitment functionality."""
    
    print("🎯 Quick Credit Commitment Test")
    print("=" * 50)
    print("Testing: C.Employed-Single with £30k income")
    print("Expected credit commitments:")
    print("  • Current repayments: £300 (1% of £30k)")
    print("  • Balance on completion: £3,000 (10% of £30k)")
    print("=" * 50)
    
    # Check credentials
    if not os.getenv("MBT_USERNAME") or not os.getenv("MBT_PASSWORD"):
        print("❌ MBT credentials not found in .env file")
        return
    
    automation = RealMBTAutomation()
    
    try:
        print("\n🚀 Starting browser...")
        await automation.start_browser()
        
        print("🔐 Logging into MBT...")
        login_success = await automation.login()
        if not login_success:
            print("❌ Login failed")
            return
        print("✅ Login successful")
        
        print("\n💳 Running credit commitment scenario...")
        result = await automation.run_single_scenario("C.Employed-Single", 30000)
        
        if result:
            print(f"\n🎉 Credit commitment test completed!")
            print(f"📊 Results:")
            print(f"   Case Type: {result['case_type']}")
            print(f"   Income: £{result['income']:,}")
            print(f"   Case Reference: {result['case_reference']}")
            print(f"   Lenders Found: {len(result['lenders_data'])}")
            
            if result['lenders_data']:
                print(f"   💰 Sample Results:")
                for lender, amount in list(result['lenders_data'].items())[:5]:
                    print(f"      {lender}: £{amount:,}")
                if len(result['lenders_data']) > 5:
                    print(f"      ... and {len(result['lenders_data']) - 5} more lenders")
                print(f"\n✅ SUCCESS: Credit commitment scenario working!")
            else:
                print(f"   ⚠️  No lender results found - check if automation completed properly")
        else:
            print("❌ Credit scenario test failed")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        print("📋 Full error details:")
        print(traceback.format_exc())
    
    finally:
        print("\n🔄 Closing browser...")
        await automation.close()
        print("✅ Test completed")

if __name__ == "__main__":
    print("Starting quick credit commitment test...")
    asyncio.run(quick_credit_test())