#!/usr/bin/env python3
"""
Test high income joint scenarios that were failing
"""

import asyncio
from real_mbt_automation import RealMBTAutomation

async def test_high_income_scenario(case_type, income, description):
    """Test a high income scenario with detailed timing info."""
    print(f"\n{'='*80}")
    print(f"🧪 TESTING HIGH INCOME: {description}")
    print(f"   Case Type: {case_type}")
    print(f"   Income: £{income:,}")
    print(f"{'='*80}")
    
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
        
        # Run scenario
        result = await automation.run_single_scenario(case_type, income)
        
        if result and result.get('lenders_data'):
            lenders_count = len(result['lenders_data'])
            gen_h = result['lenders_data'].get('Gen H', 0)
            
            print(f"\n🎉 SUCCESS!")
            print(f"   Lenders found: {lenders_count}")
            print(f"   Gen H: £{gen_h:,}")
            
            if lenders_count >= 12:
                print("   ✅ Good lender count (12+ found)")
                return True
            else:
                print(f"   ⚠️ Low lender count ({lenders_count} found)")
                return False
        else:
            print("❌ FAILURE: No results obtained")
            return False
            
    except Exception as e:
        print(f"❌ FAILURE: Exception: {e}")
        return False
        
    finally:
        await automation.close()

async def test_problematic_scenarios():
    """Test the specific scenarios that were failing."""
    
    # Focus on the high income joint scenarios that were failing
    test_scenarios = [
        # Joint scenarios at higher income levels
        ("E.Joint", 120000, "Joint Employed £120k total (£60k each)"),
        ("S.Joint", 120000, "Joint Self-Employed £120k total (£60k each)"),
        ("E.Joint", 160000, "Joint Employed £160k total (£80k each)"), 
        ("S.Joint", 160000, "Joint Self-Employed £160k total (£80k each)"),
        ("S.Joint", 200000, "Joint Self-Employed £200k total (£100k each)"),
    ]
    
    results = []
    
    for case_type, income, description in test_scenarios:
        success = await test_high_income_scenario(case_type, income, description)
        results.append((description, success))
        
        # Longer wait between high income scenarios
        print("\n⏳ Waiting 60 seconds before next high income test...")
        await asyncio.sleep(60)
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 HIGH INCOME TEST SUMMARY")
    print(f"{'='*80}")
    
    successful = 0
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {description}")
        if success:
            successful += 1
    
    print(f"\nOverall: {successful}/{len(results)} high income scenarios successful")
    print(f"Success rate: {(successful / len(results) * 100):.1f}%")
    
    if successful == len(results):
        print("🎉 All high income scenarios working!")
    else:
        print("⚠️ Some scenarios still failing - may need longer wait times")

if __name__ == "__main__":
    asyncio.run(test_problematic_scenarios())