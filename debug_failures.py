#!/usr/bin/env python3
"""
Debug why scenarios are failing
"""

import asyncio
from real_mbt_automation import RealMBTAutomation

async def test_with_debug(case_type, income, description):
    """Test a scenario with detailed debugging."""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {description}")
    print(f"   Case Type: {case_type}")
    print(f"   Income: £{income:,}")
    print(f"{'='*60}")
    
    automation = RealMBTAutomation()
    
    try:
        await automation.start_browser()
        
        # Login
        print("🔐 Logging in...")
        login_success = await automation.login()
        if not login_success:
            print("❌ FAILURE: Login failed")
            return False
        
        print("✅ Login successful")
        
        # Run scenario with detailed tracking
        result = await automation.run_single_scenario(case_type, income)
        
        if result and result.get('lenders_data'):
            lenders_count = len(result['lenders_data'])
            print(f"✅ SUCCESS: Found {lenders_count} lenders")
            return True
        else:
            print("❌ FAILURE: No lender data returned")
            print(f"   Result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ FAILURE: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await automation.close()

async def run_failure_tests():
    """Test different scenario types to identify failure patterns."""
    
    test_scenarios = [
        # Test each case type
        ("E.Single", 30000, "Single Employed £30k"),
        ("S.Single", 30000, "Single Self-Employed £30k"), 
        ("E.Joint", 60000, "Joint Employed £60k"),
        ("S.Joint", 60000, "Joint Self-Employed £60k"),
        
        # Test edge cases
        ("E.Single", 20000, "Low Income Single Employed"),
        ("E.Single", 100000, "High Income Single Employed"),
        ("S.Joint", 200000, "High Income Joint Self-Employed"),
    ]
    
    results = []
    
    for case_type, income, description in test_scenarios:
        success = await test_with_debug(case_type, income, description)
        results.append((description, success))
        
        # Wait between tests to avoid overwhelming the system
        print("\n⏳ Waiting 30 seconds before next test...")
        await asyncio.sleep(30)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    successful = 0
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {description}")
        if success:
            successful += 1
    
    print(f"\nOverall: {successful}/{len(results)} scenarios successful")
    print(f"Failure rate: {((len(results) - successful) / len(results) * 100):.1f}%")

if __name__ == "__main__":
    asyncio.run(run_failure_tests())