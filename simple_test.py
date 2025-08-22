import asyncio
from real_mbt_automation import RealMBTAutomation

async def test():
    automation = RealMBTAutomation()
    await automation.start_browser()
    
    # Login
    login_ok = await automation.login()
    if not login_ok:
        print("Login failed")
        return
    
    # Test the joint self-employed £200k scenario
    print("Testing joint self-employed £200k...")
    result = await automation.run_single_scenario("S.Joint", 200000)
    
    if result:
        print("SUCCESS!")
        print(f"Lenders found: {len(result.get('lenders_data', {}))}")
        for lender, amount in result.get('lenders_data', {}).items():
            print(f"  {lender}: £{amount:,}")
    else:
        print("FAILED")
    
    await automation.close()

if __name__ == "__main__":
    asyncio.run(test())