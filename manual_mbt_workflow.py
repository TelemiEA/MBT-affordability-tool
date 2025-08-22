#!/usr/bin/env python3
"""
Manual MBT workflow to understand the correct process for multiple scenarios.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def manual_mbt_workflow():
    """Walk through MBT workflow manually to understand best practices."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=3000)
        page = await browser.new_page()
        
        try:
            # Login
            print("🔐 Logging in...")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            print("✅ Logged in successfully!")
            
            # Key Questions to Answer:
            print("\n🔍 INVESTIGATION: Understanding MBT Workflow")
            print("\n📋 Key Questions:")
            print("1. Should we create a NEW case for each scenario?")
            print("2. Or can we modify ONE case and re-run calculations?")
            print("3. What are the EXACT field names for income inputs?")
            print("4. How do we verify that our numbers are actually being used?")
            
            # Manual Investigation Phase
            scenarios_to_test = [
                {
                    'name': 'Joint Vanilla £40k Each',
                    'applicants': 2,
                    'income1': 40000,
                    'income2': 40000,
                    'employment': 'employed'
                },
                {
                    'name': 'Single Self-Employed £40k',
                    'applicants': 1,
                    'income1': 40000,
                    'income2': None,
                    'employment': 'self_employed'
                }
            ]
            
            for i, scenario in enumerate(scenarios_to_test):
                print(f"\n🎯 SCENARIO {i+1}: {scenario['name']}")
                print("=" * 50)
                
                # Create NEW case for each scenario (testing approach 1)
                print("📝 Creating NEW RESI case...")
                await page.click('text=Create RESI Case')
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(3000)
                
                # Take screenshot of empty form
                await page.screenshot(path=f"scenario_{i+1}_empty_form.png")
                print(f"📸 Screenshot: scenario_{i+1}_empty_form.png")
                
                print("\n👀 MANUAL VERIFICATION NEEDED:")
                print("1. Look at the form - what fields are visible?")
                print("2. Are there tabs or sections we need to navigate?")
                print("3. What's the EXACT workflow to input scenario data?")
                
                print(f"\n📊 Target Inputs for {scenario['name']}:")
                print(f"   - Number of applicants: {scenario['applicants']}")
                print(f"   - Applicant 1 income: £{scenario['income1']:,}")
                if scenario['income2']:
                    print(f"   - Applicant 2 income: £{scenario['income2']:,}")
                print(f"   - Employment type: {scenario['employment']}")
                
                # Fill basic details - MINIMUM required
                print("\n📝 Filling BASIC details only...")
                try:
                    await page.fill('input[name="firstname"]', f'Test{i+1}')
                    await page.fill('input[name="surname"]', 'User')
                    await page.fill('input[name="email"]', f'test{i+1}@example.com')
                    print("✅ Basic details filled")
                except Exception as e:
                    print(f"❌ Error filling basic details: {e}")
                
                # PAUSE for manual inspection
                print(f"\n⏸️  PAUSED FOR MANUAL INSPECTION - Scenario {i+1}")
                print("🔍 Please manually:")
                print("1. Complete this scenario in the browser")
                print("2. Note which fields you fill and their exact names") 
                print("3. See if results appear immediately or after clicking Submit")
                print("4. Check if you need to create a new case for the next scenario")
                print("\n⏳ Waiting 2 minutes for manual completion...")
                
                await page.wait_for_timeout(120000)  # 2 minutes
                
                # After manual completion, take screenshot
                await page.screenshot(path=f"scenario_{i+1}_after_manual.png")
                print(f"📸 Screenshot: scenario_{i+1}_after_manual.png")
                
                # Try to detect if we're on results page
                current_url = page.url
                print(f"📍 Current URL: {current_url}")
                
                if "result" in current_url.lower() or "quote" in current_url.lower():
                    print("🎯 Detected results page!")
                    
                    # Try to extract a few sample results
                    page_text = await page.text_content('body')
                    
                    # Look for lender names and amounts
                    import re
                    lender_amounts = {}
                    
                    for lender in ['Gen H', 'Accord', 'Skipton', 'Kensington']:
                        pattern = rf'{lender}.*?£([\d,]+)'
                        match = re.search(pattern, page_text, re.IGNORECASE)
                        if match:
                            amount = match.group(1).replace(',', '')
                            lender_amounts[lender] = amount
                            print(f"   {lender}: £{amount}")
                    
                    if lender_amounts:
                        print(f"✅ Extracted {len(lender_amounts)} lender results")
                    else:
                        print("❌ No lender results found in page text")
                
                # Preparation for next scenario
                if i < len(scenarios_to_test) - 1:
                    print(f"\n🔄 Preparing for next scenario...")
                    print("Should we:")
                    print("A) Go back to dashboard and create NEW case?")
                    print("B) Modify current case and re-run?")
                    
                    choice = input("Enter A or B (or C to continue inspection): ").upper()
                    
                    if choice == 'A':
                        # Go back to dashboard
                        await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
                        await page.wait_for_load_state("networkidle")
                        print("↩️ Returned to dashboard for new case")
                    elif choice == 'B':
                        print("🔄 Staying on current page to modify case")
                    else:
                        print("🔍 Continuing with current inspection")
            
            print("\n✅ INVESTIGATION COMPLETE")
            print("\nKey Findings to Document:")
            print("1. Exact workflow for each scenario type")
            print("2. Field names and input requirements") 
            print("3. Whether to create new cases vs modify existing")
            print("4. How to verify our inputs are being used correctly")
            print("5. Results extraction methodology")
            
        except Exception as e:
            print(f"❌ Error during investigation: {e}")
            await page.screenshot(path="investigation_error.png")
            
        finally:
            print("\n⏳ Keeping browser open for final inspection...")
            await page.wait_for_timeout(30000)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(manual_mbt_workflow())