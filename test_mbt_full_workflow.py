#!/usr/bin/env python3
"""
Test complete MBT affordability workflow.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def test_full_affordability_workflow():
    """Test the complete affordability workflow in MBT."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1500)
        page = await browser.new_page()
        
        try:
            # Login
            print("🔐 Logging into MBT...")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            print("✅ Login successful!")
            
            # Start new RESI case
            print("\n📝 Creating new RESI case...")
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)
            
            # Fill First Applicant details
            print("👤 Filling First Applicant details...")
            await page.fill('input[name*="first"], input[id*="first"]', 'John')
            await page.fill('input[name*="surname"], input[id*="surname"]', 'Doe')
            await page.fill('input[name*="email"], input[id*="email"]', 'john.doe@test.com')
            
            await page.screenshot(path="step1_applicant.png")
            
            # Navigate to next step - look for Next button or arrow
            next_buttons = [
                'button:has-text("Next")',
                'button[title*="next"]',
                '.next-button',
                '[data-testid*="next"]',
                'button[type="submit"]'
            ]
            
            next_clicked = False
            for selector in next_buttons:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        print(f"Found next button: {selector}")
                        await button.click()
                        await page.wait_for_timeout(2000)
                        next_clicked = True
                        break
                except:
                    continue
            
            # Try clicking the forward arrow at bottom
            if not next_clicked:
                try:
                    # Look for arrow buttons at the bottom
                    arrow_button = await page.query_selector('button:has-text("▶"), button[title*="forward"], .arrow-right')
                    if arrow_button:
                        print("Clicking forward arrow...")
                        await arrow_button.click()
                        await page.wait_for_timeout(2000)
                        next_clicked = True
                except:
                    pass
            
            if next_clicked:
                await page.screenshot(path="step2_after_next.png")
                print("✅ Moved to next step")
                
                # Check what's on this page
                page_content = await page.content()
                
                # Look for income-related fields
                income_keywords = ['income', 'salary', 'earnings', 'employment', 'occupation']
                found_keywords = [k for k in income_keywords if k in page_content.lower()]
                print(f"Found income keywords: {found_keywords}")
                
                # Look for specific input fields we might need to fill
                income_fields = await page.query_selector_all('input[name*="income"], input[id*="income"], input[placeholder*="income"]')
                salary_fields = await page.query_selector_all('input[name*="salary"], input[id*="salary"], input[placeholder*="salary"]')
                employment_fields = await page.query_selector_all('select[name*="employment"], select[id*="employment"]')
                
                print(f"Found {len(income_fields)} income fields")
                print(f"Found {len(salary_fields)} salary fields") 
                print(f"Found {len(employment_fields)} employment fields")
                
                # Try to fill income if we find the field
                if income_fields:
                    print("💰 Filling income field...")
                    await income_fields[0].fill('40000')
                elif salary_fields:
                    print("💰 Filling salary field...")
                    await salary_fields[0].fill('40000')
                
                # Look for employment type dropdown
                if employment_fields:
                    print("👔 Setting employment type...")
                    try:
                        await employment_fields[0].select_option('Employed')
                    except:
                        try:
                            await employment_fields[0].select_option('employed')
                        except:
                            print("Could not set employment type")
                
                # Continue to next step
                print("\n➡️ Looking for next step...")
                for selector in next_buttons:
                    try:
                        button = await page.query_selector(selector)
                        if button:
                            await button.click()
                            await page.wait_for_timeout(2000)
                            break
                    except:
                        continue
                
                await page.screenshot(path="step3_income_filled.png")
                
                # Keep going through the workflow to find the affordability calculation
                step_count = 3
                while step_count < 10:  # Prevent infinite loop
                    print(f"\n🔍 Step {step_count}: Exploring current page...")
                    
                    current_url = page.url
                    page_content = await page.content()
                    
                    # Check for affordability/calculation related content
                    calc_keywords = [
                        'affordability', 'calculate', 'borrowing', 'mortgage amount', 
                        'loan amount', 'maximum', 'assessment', 'criteria'
                    ]
                    
                    found_calc_keywords = [k for k in calc_keywords if k in page_content.lower()]
                    if found_calc_keywords:
                        print(f"✅ Found calculation keywords: {found_calc_keywords}")
                        
                        # Look for calculate/run buttons
                        calc_buttons = await page.query_selector_all(
                            'button:has-text("Calculate"), button:has-text("Run"), button:has-text("Check"), button:has-text("Search")'
                        )
                        
                        if calc_buttons:
                            print(f"🎯 Found {len(calc_buttons)} calculation buttons!")
                            for i, button in enumerate(calc_buttons):
                                text = await button.text_content()
                                print(f"  Button {i+1}: {text}")
                            
                            # Click the first calculation button
                            print("🚀 Running affordability calculation...")
                            await calc_buttons[0].click()
                            await page.wait_for_timeout(5000)  # Wait for results
                            
                            await page.screenshot(path="step_calculation_results.png")
                            
                            # Look for results
                            print("📊 Looking for lender results...")
                            
                            # Common patterns for lender results
                            result_selectors = [
                                'table tr',
                                '.result',
                                '.lender',
                                '[data-testid*="result"]',
                                '.mortgage-result',
                                '.loan-result'
                            ]
                            
                            lender_results = {}
                            
                            for selector in result_selectors:
                                try:
                                    elements = await page.query_selector_all(selector)
                                    if len(elements) > 5:  # Likely a results table
                                        print(f"Found {len(elements)} result elements with selector: {selector}")
                                        
                                        for element in elements[:15]:  # Check first 15
                                            text = await element.text_content()
                                            if text and any(lender in text for lender in [
                                                'Accord', 'Skipton', 'Kensington', 'Precise', 'Atom',
                                                'Metro', 'Nottingham', 'Leeds', 'Santander', 'Gen H'
                                            ]):
                                                print(f"  Found lender result: {text[:100]}...")
                                        break
                                except:
                                    continue
                            
                            # Also check page content for specific amounts
                            import re
                            amounts = re.findall(r'£[\d,]+', page_content)
                            if amounts:
                                print(f"Found amounts on page: {amounts[:10]}")
                            
                            break
                    
                    # Try to go to next step
                    next_found = False
                    for selector in next_buttons:
                        try:
                            button = await page.query_selector(selector)
                            if button and await button.is_visible():
                                await button.click()
                                await page.wait_for_timeout(2000)
                                next_found = True
                                break
                        except:
                            continue
                    
                    if not next_found:
                        print("No more next buttons found - end of workflow")
                        break
                    
                    step_count += 1
                    await page.screenshot(path=f"step_{step_count}.png")
            
            else:
                print("❌ Could not find next button to proceed")
            
            print("\n🔍 Keeping browser open for 60 seconds for manual exploration...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error during workflow test: {e}")
            await page.screenshot(path="mbt_workflow_error.png")
            import traceback
            traceback.print_exc()
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_full_affordability_workflow())