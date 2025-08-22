"""
Quick fix to complete the specific dropdowns blocking progress.
Based on the exact validation errors we can see in the screenshot.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def fix_dropdowns():
    """Fix the specific dropdowns causing validation errors."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            # Login and navigate to form
            print("🔐 Quick login...")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            # Create case and quick progression to the dropdown section
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
            # Fill basic fields
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
            
            # Submit to progress to dropdown section
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(3000)
                
                # Dismiss modal
                try:
                    ok_button = await page.query_selector('button:has-text("OK")')
                    if ok_button and await ok_button.is_visible():
                        await ok_button.click()
                        await page.wait_for_timeout(1000)
                except:
                    pass
                
                await page.wait_for_load_state("networkidle")
            
            # Now we should be at the Property and Mortgage section
            print("🎯 At Property and Mortgage section - fixing specific dropdowns...")
            
            # Take screenshot to confirm location
            await page.screenshot(path="dropdown_fix_location.png")
            
            # 1. Fix "Reason for Mortgage" dropdown
            print("📋 Fixing Reason for Mortgage dropdown...")
            all_selects = await page.query_selector_all('select')
            print(f"Found {len(all_selects)} select elements")
            
            for i, select in enumerate(all_selects):
                try:
                    # Check if this is the reason dropdown by looking at validation text
                    parent = await select.query_selector('xpath=..')
                    if parent:
                        parent_text = await parent.text_content()
                        if 'reason' in parent_text.lower() and 'mortgage' in parent_text.lower():
                            print(f"🎯 Found Reason for Mortgage dropdown (select {i+1})")
                            
                            # Get options
                            options = await select.query_selector_all('option')
                            option_texts = []
                            for option in options:
                                text = await option.text_content()
                                value = await option.get_attribute('value')
                                option_texts.append(f"'{text}' (value: {value})")
                            
                            print(f"   Options: {option_texts}")
                            
                            # Try to select 'Purchase' or similar
                            for purchase_option in ['Purchase', 'purchase', 'Buy', 'buy', 'Buying', 'buying']:
                                try:
                                    await select.select_option(purchase_option)
                                    print(f"✅ Set Reason for Mortgage to: {purchase_option}")
                                    await page.wait_for_timeout(1000)
                                    break
                                except:
                                    continue
                            else:
                                # Select first non-empty option
                                if len(options) > 1:
                                    try:
                                        await select.select_option(index=1)
                                        selected_text = await select.input_value()
                                        print(f"✅ Set Reason for Mortgage to first option: {selected_text}")
                                    except:
                                        pass
                            break
                except:
                    continue
            
            # 2. Fix "Property Type" dropdown
            print("🏠 Fixing Property Type dropdown...")
            for i, select in enumerate(all_selects):
                try:
                    parent = await select.query_selector('xpath=..')
                    if parent:
                        parent_text = await parent.text_content()
                        if 'property' in parent_text.lower() and 'type' in parent_text.lower():
                            print(f"🎯 Found Property Type dropdown (select {i+1})")
                            
                            # Get options
                            options = await select.query_selector_all('option')
                            option_texts = []
                            for option in options:
                                text = await option.text_content()
                                option_texts.append(text)
                            
                            print(f"   Options: {option_texts}")
                            
                            # Try to select 'House' or similar
                            for house_option in ['House', 'house', 'Detached', 'detached', 'Semi']:
                                try:
                                    await select.select_option(house_option)
                                    print(f"✅ Set Property Type to: {house_option}")
                                    await page.wait_for_timeout(1000)
                                    break
                                except:
                                    continue
                            else:
                                # Select first non-empty option
                                if len(options) > 1:
                                    try:
                                        await select.select_option(index=1)
                                        selected_text = await select.input_value()
                                        print(f"✅ Set Property Type to first option: {selected_text}")
                                    except:
                                        pass
                            break
                except:
                    continue
            
            # 3. Fix "Tenure" radio buttons
            print("🏛️ Fixing Tenure radio button...")
            freehold_radio = await page.query_selector('input[type="radio"][value="Freehold"], input[type="radio"][value="freehold"]')
            if freehold_radio:
                try:
                    await freehold_radio.check()
                    print("✅ Set Tenure to Freehold")
                except:
                    pass
            else:
                # Try to find by text content
                radios = await page.query_selector_all('input[type="radio"]')
                for radio in radios:
                    try:
                        parent = await radio.query_selector('xpath=..')
                        if parent:
                            text = await parent.text_content()
                            if 'freehold' in text.lower():
                                await radio.check()
                                print("✅ Set Tenure to Freehold (by text)")
                                break
                    except:
                        continue
            
            # Take screenshot after fixes
            await page.screenshot(path="after_dropdown_fixes.png")
            
            # Try to submit again
            print("🚀 Submitting after dropdown fixes...")
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                # Handle any modals
                try:
                    ok_button = await page.query_selector('button:has-text("OK")')
                    if ok_button and await ok_button.is_visible():
                        await ok_button.click()
                        await page.wait_for_timeout(2000)
                except:
                    pass
                
                await page.wait_for_load_state("networkidle")
                
                # Take screenshot of result
                await page.screenshot(path="after_fixes_submit.png")
                
                # Check if we progressed
                page_text = await page.text_content('body')
                if 'please' not in page_text.lower() or 'validation' not in page_text.lower():
                    print("🎉 SUCCESS! Validation errors resolved!")
                    
                    # Look for income fields
                    income_fields = await page.query_selector_all('input[name*="income"], input[name*="salary"]')
                    visible_income = 0
                    for field in income_fields:
                        if await field.is_visible():
                            visible_income += 1
                    
                    print(f"Found {visible_income} VISIBLE income fields!")
                    
                    if visible_income > 0:
                        print("🎉 BREAKTHROUGH! We have visible income fields!")
                else:
                    print("⚠️ Still have validation errors")
                
                print(f"Current URL: {page.url}")
            
            # Keep browser open for inspection
            print("⏳ Keeping browser open for 60 seconds...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="dropdown_fix_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(fix_dropdowns())