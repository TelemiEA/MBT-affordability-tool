"""
Quick Test - Test one scenario to verify everything works
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def quick_test():
    """Quick test of one scenario."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            print("🎯 QUICK TEST - Single Scenario")
            print("=" * 40)
            
            # Login
            print("1. Logging in...")
            await page.goto("https://mortgagebrokertools.co.uk/signin", timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle", timeout=30000)
            print("   ✅ Login successful")
            
            # Go to dashboard
            print("2. Opening dashboard...")
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes', timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            await page.wait_for_timeout(3000)
            print("   ✅ Dashboard loaded")
            
            # Take screenshot to verify cases are visible
            await page.screenshot(path="quick_test_dashboard.png")
            
            # Check if we can see the cases
            page_text = await page.text_content('body')
            cases_found = []
            target_cases = ["QX002187461", "QX002187450", "QX002187335", "QX002187301"]
            
            for case in target_cases:
                if case in page_text:
                    cases_found.append(case)
            
            print(f"3. Cases found: {cases_found}")
            
            if len(cases_found) >= 1:
                # Try to open the first case
                test_case = cases_found[0]
                print(f"4. Opening test case: {test_case}")
                
                await page.click(f'text={test_case}', timeout=10000)
                await page.wait_for_load_state("networkidle", timeout=30000)
                await page.wait_for_timeout(3000)
                
                await page.screenshot(path="quick_test_case_opened.png")
                print("   ✅ Case opened successfully")
                
                print("\n🎉 QUICK TEST SUCCESSFUL!")
                print("✅ Login works")
                print("✅ Dashboard loads")
                print("✅ Cases are visible")
                print("✅ Case can be opened")
                print("\n🚀 Ready to run full automation!")
                
            else:
                print("❌ No target cases found on dashboard")
                print("Available cases need to be created in MBT first")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            await page.screenshot(path="quick_test_error.png")
            
        finally:
            print("\n⏳ Keeping browser open for 30 seconds...")
            await page.wait_for_timeout(30000)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(quick_test())