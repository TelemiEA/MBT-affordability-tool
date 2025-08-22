"""
Quick test to fill the specific required fields that are showing validation errors.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def test_specific_fields():
    """Test filling the specific required fields that are failing validation."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            # Login and navigate to the case that's already progressed
            print("🔐 Logging into MBT...")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            if "signin" in page.url.lower():
                print("❌ Login failed")
                return
            
            print("✅ Login successful")
            
            # Navigate to an existing case or create new one
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            
            # Create new case
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
            print(f"✅ Case created: {page.url}")
            
            # Fill basic required fields to progress to the problem section
            basic_fields = [
                ('input[name="firstname"]', 'Test'),
                ('input[name="surname"]', 'User'),
                ('input[name="email"]', 'test@example.com'),
                ('input[name="purchase"]', '1000000'),
                ('input[name="loan_amount"]', '100000')
            ]
            
            for selector, value in basic_fields:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await field.fill(value)
                        print(f"✅ Filled {selector}")
                except:
                    pass
            
            # Check joint application
            joint_checkbox = await page.query_selector('input[type="checkbox"]')
            if joint_checkbox:
                await joint_checkbox.check()
                print("✅ Checked joint application")
                await page.wait_for_timeout(2000)
            
            # Continue to mortgage preferences section
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                print("✅ Progressed to next section")
            
            # Now handle the specific validation errors
            print("🎯 Filling specific required fields...")
            
            # 1. Reason for Mortgage
            print("📋 Setting Reason for Mortgage...")
            reason_dropdown = await page.query_selector('select')
            if reason_dropdown:
                options = await reason_dropdown.query_selector_all('option')
                if len(options) > 1:
                    # Select the first non-empty option
                    await reason_dropdown.select_option(index=1)
                    print("✅ Selected reason for mortgage")
            
            # 2. Property Type
            print("🏠 Setting Property Type...")
            all_selects = await page.query_selector_all('select')
            for select in all_selects:
                name = await select.get_attribute('name')
                if name and 'type' in name.lower():
                    options = await select.query_selector_all('option')
                    if len(options) > 1:
                        await select.select_option(index=1)
                        print("✅ Selected property type")
                        break
            
            # 3. Tenure (Freehold radio button)
            print("🏛️ Setting Tenure...")
            freehold_radio = await page.query_selector('input[type="radio"][value*="Freehold"]')
            if freehold_radio:
                await freehold_radio.check()
                print("✅ Selected Freehold tenure")
            else:
                # Try finding by text
                radios = await page.query_selector_all('input[type="radio"]')
                for radio in radios:
                    parent = await radio.query_selector('xpath=..')
                    if parent:
                        text = await parent.text_content()
                        if text and 'freehold' in text.lower():
                            await radio.check()
                            print("✅ Selected Freehold tenure (by text)")
                            break
            
            # Take screenshot before final attempt
            await page.screenshot(path="before_final_attempt.png")
            print("📸 Screenshot saved before final attempt")
            
            # Try to submit again
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(10000)
                
                # Take final screenshot
                await page.screenshot(path="final_attempt_result.png")
                print("📸 Final result screenshot saved")
                
                # Check for progress
                current_url = page.url
                print(f"Final URL: {current_url}")
                
                # Look for results or next section
                page_text = await page.text_content('body')
                if 'results' in page_text.lower() or 'lender' in page_text.lower():
                    print("🎉 SUCCESS - Reached results section!")
                else:
                    print("⚠️ Still on form - may need more fields")
            
            # Keep browser open for inspection
            print("⏳ Keeping browser open for 60 seconds...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="error_screenshot.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_specific_fields())