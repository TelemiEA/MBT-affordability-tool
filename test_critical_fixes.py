#!/usr/bin/env python3
"""
Test the critical fixes for joint self-employed income splitting and wait times
"""

import asyncio
from real_mbt_automation import RealMBTAutomation

async def test_critical_joint_scenario():
    """Test a joint self-employed scenario to verify income splitting and wait times."""
    
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
        
        # Test the problematic joint self-employed £200k scenario
        print("\n" + "="*80)
        print("🧪 TESTING CRITICAL FIX: Joint Self-Employed £200k")
        print("   Expected behavior:")
        print("   - Total income: £200,000")
        print("   - Each applicant should get: £100,000")
        print("   - App1 last year profit: £100,000")
        print("   - App1 two year profit: £50,000")
        print("   - App2 salary: £100,000")
        print("   - Wait time: ~9 minutes (3 min base × 6.7 income mult × 3.0 joint mult)")
        print("="*80)
        
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
                print(f"   {i:2d}. {lender:15s}: £{amount:,}{marker}")
            
            # Evaluate success
            if lenders_count >= 15:
                print("\n✅ EXCELLENT! Found 15+ lenders - wait time fix working!")
                return True
            elif lenders_count >= 12:
                print("\n✅ GOOD! Found 12+ lenders - significant improvement!")
                return True
            else:
                print(f"\n⚠️ Still only {lenders_count} lenders - may need even longer waits")
                return False
                
        else:
            print("❌ FAILURE: No results obtained")
            return False
            
    except Exception as e:
        print(f"❌ FAILURE: Exception: {e}")
        return False
        
    finally:
        await automation.close()

async def test_multiple_joint_scenarios():
    """Test multiple joint scenarios to verify fixes."""
    
    test_scenarios = [
        ("S.Joint", 120000, "Joint Self-Employed £120k total (£60k each)"),
        ("S.Joint", 200000, "Joint Self-Employed £200k total (£100k each)"),
        ("E.Joint", 160000, "Joint Employed £160k total (£80k each)"),
    ]
    
    results = []
    
    for case_type, income, description in test_scenarios:
        print(f"\n{'='*80}")
        print(f"🧪 TESTING: {description}")
        print(f"{'='*80}")
        
        automation = RealMBTAutomation()
        
        try:
            await automation.start_browser()
            
            login_success = await automation.login()
            if not login_success:
                print("❌ Login failed")
                results.append((description, False, "Login failed"))
                continue
            
            result = await automation.run_single_scenario(case_type, income)
            
            if result and result.get('lenders_data'):
                lenders_count = len(result['lenders_data'])
                success = lenders_count >= 12
                results.append((description, success, f"{lenders_count} lenders"))
                
                status = "✅ PASS" if success else "⚠️ PARTIAL"
                print(f"\n{status}: {lenders_count} lenders found")
            else:
                results.append((description, False, "No results"))
                print("\n❌ FAIL: No results")
                
        except Exception as e:
            results.append((description, False, f"Error: {e}"))
            print(f"\n❌ FAIL: {e}")
            
        finally:
            await automation.close()
        
        # Wait between tests
        print("\n⏳ Waiting 30 seconds before next test...")
        await asyncio.sleep(30)
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 CRITICAL FIXES TEST SUMMARY")
    print(f"{'='*80}")
    
    successful = 0
    for description, success, details in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {description} - {details}")
        if success:
            successful += 1
    
    print(f"\nOverall: {successful}/{len(results)} scenarios successful")
    print(f"Success rate: {(successful / len(results) * 100):.1f}%")
    
    if successful == len(results):
        print("🎉 All critical fixes working perfectly!")
    elif successful > 0:
        print("✅ Partial success - fixes showing improvement!")
    else:
        print("❌ Fixes not working - need further investigation")

if __name__ == "__main__":
    print("🚀 Testing critical fixes for joint scenarios and wait times...")
    
    # Choose test type
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "single":
        asyncio.run(test_critical_joint_scenario())
    else:
        asyncio.run(test_multiple_joint_scenarios())