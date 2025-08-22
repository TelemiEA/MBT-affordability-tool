"""
Fixed Case Test - Corrected field clearing and button finding
Test the basic workflow with proper Playwright syntax
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def fixed_case_test():
    """Fixed test to open E.Single case and update income properly."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=3000)
        page = await browser.new_page()
        
        try:
            print("🎯 FIXED CASE TEST - E.SINGLE")
            print("Target: QX002187461 (E. Single)")
            print("=" * 40)
            
            # Login
            await page.goto("https://mortgagebrokertools.co.uk/signin", timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle", timeout=30000)
            print("✅ Login successful")
            
            # Go to dashboard
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes', timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            await page.wait_for_timeout(3000)
            print("✅ Dashboard loaded")
            
            # Click on E.Single case
            await page.click('text=QX002187461', timeout=10000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            await page.wait_for_timeout(3000)
            print("✅ Case opened")
            
            # Take screenshot of opened case
            await page.screenshot(path="case_opened_fixed.png")
            
            # Update salary with correct syntax
            print("💰 Updating salary field...")
            await update_salary_fixed(page)
            
            # Look for Get Results button more thoroughly
            print("🚀 Looking for Get Results button...")
            await find_and_click_results_button(page)
            
            # Keep browser open for inspection
            print("\\n⏳ Keeping browser open for manual inspection...")
            await page.wait_for_timeout(120000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="fixed_test_error.png")
            
        finally:
            await browser.close()


async def update_salary_fixed(page):
    """Update salary field with correct Playwright syntax."""
    try:
        # Take screenshot to see the form
        await page.screenshot(path="before_salary_update_fixed.png")
        
        # Look specifically for the annual basic salary field
        # We know from the previous run it exists and has value £20,000
        
        # Strategy 1: Target by name if possible
        try:
            salary_field = await page.query_selector('input[name*="income_amount_primary_applicant"]')
            if salary_field and await salary_field.is_visible():
                await salary_field.fill('40000')  # Use fill() which clears automatically
                await salary_field.press('Tab')
                print("   ✅ Updated salary via name selector to £40,000")
                await page.screenshot(path="salary_updated_fixed.png")
                return True
        except Exception as e:
            print(f"   ⚠️ Name selector failed: {e}")
        
        # Strategy 2: Find field containing "annual basic salary" text
        try:
            inputs = await page.query_selector_all('input[type="text"], input[type="number"]')
            
            for input_field in inputs:
                try:
                    if not await input_field.is_visible():
                        continue
                    
                    # Get the parent container to check for label text
                    parent = await input_field.query_selector('..')
                    if parent:
                        parent_text = await parent.text_content() or ''
                        
                        if 'annual basic salary' in parent_text.lower():
                            current_value = await input_field.input_value()
                            print(f"   Found annual basic salary field, current: {current_value}")
                            
                            # Update the field
                            await input_field.fill('40000')  # This automatically clears first
                            await input_field.press('Tab')
                            print("   ✅ Updated annual basic salary to £40,000")
                            
                            await page.screenshot(path="salary_updated_fixed.png")
                            return True
                            
                except Exception as e:
                    print(f"   ⚠️ Error with input field: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ❌ Strategy 2 failed: {e}")
        
        # Strategy 3: Look for any field with current value £20,000
        try:
            inputs = await page.query_selector_all('input')
            
            for input_field in inputs:
                try:
                    if await input_field.is_visible():
                        current_value = await input_field.input_value()
                        if current_value and '20000' in current_value.replace(',', '').replace('£', ''):
                            print(f"   Found field with £20,000: {current_value}")
                            await input_field.fill('40000')
                            await input_field.press('Tab')
                            print("   ✅ Updated field to £40,000")
                            await page.screenshot(path="salary_updated_fixed.png")
                            return True
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"   ❌ Strategy 3 failed: {e}")
        
        print("   ⚠️ Could not update salary field")
        return False
        
    except Exception as e:
        print(f"   ❌ Error updating salary: {e}")
        return False


async def find_and_click_results_button(page):
    """More thorough search for Get Results button."""
    try:
        await page.screenshot(path="looking_for_button_fixed.png")
        
        # Strategy 1: Look for common button texts
        button_texts = ['Get Results', 'Run', 'Submit', 'Calculate', 'Search', 'Generate Results']
        
        for button_text in button_texts:
            try:
                await page.click(f'text="{button_text}"', timeout=3000)
                await page.wait_for_load_state("networkidle", timeout=30000)
                print(f"   ✅ Clicked button: {button_text}")
                await check_for_results(page)
                return True
            except:
                continue
        
        # Strategy 2: Look for buttons with partial text match
        try:
            buttons = await page.query_selector_all('button, input[type="submit"], input[type="button"]')
            
            for button in buttons:
                try:
                    if await button.is_visible():
                        text = await button.text_content() or ''
                        inner_text = await button.inner_text() if hasattr(button, 'inner_text') else ''
                        combined_text = (text + inner_text).lower()
                        
                        if any(term in combined_text for term in ['result', 'run', 'submit', 'calculate', 'search']):
                            print(f"   Found potential button: {text or inner_text}")
                            await button.click()
                            await page.wait_for_load_state("networkidle", timeout=30000)
                            print(f"   ✅ Clicked button: {text or inner_text}")
                            await check_for_results(page)
                            return True
                            
                except Exception as e:
                    print(f"   ⚠️ Error with button: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ❌ Strategy 2 failed: {e}")
        
        # Strategy 3: Look for any clickable element with "result" text
        try:
            clickable_elements = await page.query_selector_all('a, button, div[onclick], span[onclick]')
            
            for element in clickable_elements:
                try:
                    text = await element.text_content() or ''
                    if 'result' in text.lower() and await element.is_visible():
                        print(f"   Found clickable element: {text}")
                        await element.click()
                        await page.wait_for_load_state("networkidle", timeout=30000)
                        print(f"   ✅ Clicked element: {text}")
                        await check_for_results(page)
                        return True
                        
                except:
                    continue
                    
        except Exception as e:
            print(f"   ❌ Strategy 3 failed: {e}")
        
        print("   ⚠️ No results button found")
        return False
        
    except Exception as e:
        print(f"   ❌ Error finding results button: {e}")
        return False


async def check_for_results(page):
    """Check if we reached the results page."""
    try:
        await page.wait_for_timeout(5000)
        await page.screenshot(path="after_clicking_button_fixed.png")
        
        page_text = await page.text_content('body')
        
        if any(term in page_text.lower() for term in ['results', 'lender', 'quote', 'offers']):
            print("🎉 RESULTS PAGE DETECTED!")
            
            # Look for target lenders
            target_lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom"]
            found_lenders = [lender for lender in target_lenders if lender in page_text]
            
            if found_lenders:
                print(f"\\n🎉🎉🎉 SUCCESS! LENDERS FOUND: {found_lenders} 🎉🎉🎉")
                print(f"📊 Total lenders: {len(found_lenders)}")
                print("✅ EXISTING CASE APPROACH WORKS!")
                print("🚀 Ready to scale to all 32 scenarios!")
            else:
                print("✅ Results page reached (no target lenders visible yet)")
        else:
            print("⚠️ Results not detected yet")
            
    except Exception as e:
        print(f"   ❌ Error checking results: {e}")


if __name__ == "__main__":
    asyncio.run(fixed_case_test())