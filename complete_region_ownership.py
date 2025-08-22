"""
Focused test to complete the Region and Ownership dropdowns that are now visible.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def complete_region_ownership():
    """Complete the region and ownership fields and continue progression."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
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
            
            print("✅ Login successful")
            
            # Create new case and progress to the region/ownership section
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
            # Quick progression to reach the region/ownership section
            # Fill basic required fields
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
            
            # Progress through form sections
            for i in range(3):  # Try multiple submits to reach the right section
                # Fill any dropdowns and checkboxes
                all_selects = await page.query_selector_all('select')
                for select in all_selects:
                    try:
                        options = await select.query_selector_all('option')
                        if len(options) > 1:
                            await select.select_option(index=1)
                    except:
                        pass
                
                # Check any checkboxes for joint application
                checkboxes = await page.query_selector_all('input[type="checkbox"]')
                for checkbox in checkboxes:
                    try:
                        await checkbox.check()
                    except:
                        pass
                
                # Set radio buttons
                radios = await page.query_selector_all('input[type="radio"]')
                for radio in radios:
                    try:
                        value = await radio.get_attribute('value')
                        if value and any(val in value.lower() for val in ['yes', 'freehold', 'no']):
                            await radio.check()
                            break
                    except:
                        pass
                
                # Submit
                submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
                if submit_button:
                    await submit_button.click()
                    await page.wait_for_timeout(3000)
                    
                    # Dismiss any modals
                    try:
                        ok_button = await page.query_selector('button:has-text("OK")')
                        if ok_button and await ok_button.is_visible():
                            await ok_button.click()
                            await page.wait_for_timeout(1000)
                    except:
                        pass
                    
                    # Check if we're at the region/ownership section
                    page_text = await page.text_content('body')
                    if 'region' in page_text.lower() and 'ownership' in page_text.lower():
                        print(f"✅ Reached region/ownership section on attempt {i+1}")
                        break
                    
                    await page.wait_for_timeout(2000)
            
            # Now focus on filling the Region and Ownership dropdowns
            print("🎯 Filling Region and Ownership dropdowns...")
            
            # Take screenshot of current state
            await page.screenshot(path="before_region_ownership.png")
            
            # Fill Region dropdown
            print("🌍 Setting Region...")
            region_select = await page.query_selector('select[name*="region"], select:has-text("Region")')
            if not region_select:
                # Try finding by ID or other attributes
                all_selects = await page.query_selector_all('select')
                for select in all_selects:
                    parent_text = await page.evaluate('(element) => element.parentElement?.textContent || ""', select)
                    if 'region' in parent_text.lower():
                        region_select = select
                        break
            
            if region_select:
                try:
                    # Get available options
                    options = await region_select.query_selector_all('option')
                    option_texts = []
                    for option in options:
                        text = await option.text_content()
                        option_texts.append(text)
                    
                    print(f"Region options: {option_texts}")
                    
                    # Try common UK regions
                    for region in ['England', 'england', 'United Kingdom', 'UK', 'London', 'South East']:
                        try:
                            await region_select.select_option(region)
                            print(f"✅ Set Region to: {region}")
                            break
                        except:
                            continue
                    else:
                        # Select first non-empty option
                        if len(options) > 1:
                            await region_select.select_option(index=1)
                            print("✅ Set Region (first option)")
                except Exception as e:
                    print(f"❌ Error setting region: {e}")
            
            # Fill Ownership dropdown
            print("🏠 Setting Ownership...")
            ownership_select = await page.query_selector('select[name*="ownership"], select[name*="tenure"]')
            if not ownership_select:
                # Try finding by text context
                all_selects = await page.query_selector_all('select')
                for select in all_selects:
                    parent_text = await page.evaluate('(element) => element.parentElement?.textContent || ""', select)
                    if 'ownership' in parent_text.lower() or 'tenure' in parent_text.lower():
                        ownership_select = select
                        break
            
            if ownership_select:
                try:
                    # Get available options
                    options = await ownership_select.query_selector_all('option')
                    option_texts = []
                    for option in options:
                        text = await option.text_content()
                        option_texts.append(text)
                    
                    print(f"Ownership options: {option_texts}")
                    
                    # Try common ownership types
                    for ownership in ['Freehold', 'freehold', 'Owner', 'owner']:
                        try:
                            await ownership_select.select_option(ownership)
                            print(f"✅ Set Ownership to: {ownership}")
                            break
                        except:
                            continue
                    else:
                        # Select first non-empty option
                        if len(options) > 1:
                            await ownership_select.select_option(index=1)
                            print("✅ Set Ownership (first option)")
                except Exception as e:
                    print(f"❌ Error setting ownership: {e}")
            
            # Take screenshot after filling
            await page.screenshot(path="after_region_ownership.png")
            
            # Submit to continue
            print("🚀 Submitting to continue...")
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
                
                # Take screenshot of next section
                await page.screenshot(path="next_section.png")
                print("📸 Screenshot of next section saved")
                
                # Check what section we're on now
                page_text = await page.text_content('body')
                if 'applicant' in page_text.lower() or 'employment' in page_text.lower() or 'income' in page_text.lower():
                    print("🎉 SUCCESS! Reached applicant/employment section!")
                else:
                    print("⚠️ Not yet at applicant section, may need more fields")
                
                print(f"Current URL: {page.url}")
            
            # Keep browser open for inspection
            print("⏳ Keeping browser open for 60 seconds...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="completion_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(complete_region_ownership())