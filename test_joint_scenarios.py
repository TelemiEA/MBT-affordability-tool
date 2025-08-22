"""
Test Joint Applicant Scenarios
"""

import asyncio
from real_mbt_automation import RealMBTAutomation

async def test_joint_scenarios():
    """Test joint applicant scenarios to verify both applicants' incomes are updated."""
    
    automation = RealMBTAutomation()
    
    try:
        await automation.start_browser()
        
        # Test login
        login_success = await automation.login()
        if not login_success:
            print("❌ Login failed")
            return
        
        print("✅ Login successful")
        
        # Test 1: Joint Employed
        print("\n🧪 Testing Joint Employed (E.Joint) with £60k total income...")
        print("   Expected: Applicant 1 = £30k, Applicant 2 = £30k")
        
        result1 = await automation.run_single_scenario("E.Joint", 60000)
        
        if result1:
            print("✅ Joint employed test completed")
            print(f"   Found {len(result1.get('lenders_data', {}))} lenders")
        else:
            print("❌ Joint employed test failed")
        
        # Test 2: Joint Self-Employed + Employed  
        print("\n🧪 Testing Joint Self-Employed (S.Joint) with £50k total income...")
        print("   Expected: Applicant 1 (self-emp) = Last £50k, Two years £25k")
        print("             Applicant 2 (employed) = £50k")
        
        result2 = await automation.run_single_scenario("S.Joint", 50000)
        
        if result2:
            print("✅ Joint self-employed test completed")
            print(f"   Found {len(result2.get('lenders_data', {}))} lenders")
        else:
            print("❌ Joint self-employed test failed")
            
        print("\n🎉 Joint scenario testing complete!")
        print("Check the screenshots and logs to verify both applicants' incomes were updated correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        await automation.close()

if __name__ == "__main__":
    asyncio.run(test_joint_scenarios())