"""
Simple Case Test - Focus on just opening one case and updating income
Test the basic workflow with the E.Single case
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def simple_case_test():
    """Simple test to open E.Single case and update income."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=3000)
        page = await browser.new_page()
        
        try:
            print("🎯 SIMPLE CASE TEST - E.SINGLE")
            print("Target: QX002187461 (E. Single)")
            print("=" * 40)
            
            # Login with shorter timeouts
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
            
            # Take screenshot
            await page.screenshot(path="simple_test_dashboard.png")
            
            # Try to click on E.Single case (QX002187461)
            print("🔍 Looking for QX002187461...")
            
            # Multiple strategies to click the case
            case_opened = False
            
            # Strategy 1: Direct text click
            try:
                await page.click('text=QX002187461', timeout=10000)
                await page.wait_for_load_state("networkidle", timeout=30000)
                case_opened = True
                print("✅ Case opened via direct text click")
            except Exception as e:
                print(f"   ❌ Direct text click failed: {e}")
            
            # Strategy 2: Link selector
            if not case_opened:
                try:
                    await page.click('a:has-text("QX002187461")', timeout=10000)
                    await page.wait_for_load_state("networkidle", timeout=30000)
                    case_opened = True
                    print("✅ Case opened via link selector")
                except Exception as e:
                    print(f"   ❌ Link selector failed: {e}")
            
            # Strategy 3: Look for any clickable element with that text
            if not case_opened:
                try:
                    elements = await page.query_selector_all('*')
                    for element in elements[:50]:  # Limit search
                        try:
                            text = await element.text_content()
                            if text and 'QX002187461' in text:
                                await element.click()
                                await page.wait_for_load_state("networkidle", timeout=30000)
                                case_opened = True
                                print("✅ Case opened via element search")
                                break
                        except:
                            continue
                except Exception as e:
                    print(f"   ❌ Element search failed: {e}")
            
            if case_opened:
                await page.wait_for_timeout(3000)
                await page.screenshot(path="case_opened.png")
                print("🎉 Case successfully opened!")
                
                # Try to find and update salary field
                print("💰 Looking for salary field...")
                await update_salary_simple(page)
                
                # Look for Get Results button
                print("🚀 Looking for Get Results button...")
                await click_get_results(page)
                
            else:
                print("❌ Could not open the case")
            
            # Keep browser open for inspection
            print("\n⏳ Keeping browser open for manual inspection...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="simple_test_error.png")
            
        finally:
            await browser.close()


async def update_salary_simple(page):
    """Simple salary update approach."""
    try:
        # Take screenshot to see the form
        await page.screenshot(path="before_salary_update.png")
        
        # Look for input fields that might be salary
        inputs = await page.query_selector_all('input[type="text"], input[type="number"]')
        
        salary_updated = False
        for input_field in inputs:
            try:
                if not await input_field.is_visible():
                    continue
                
                # Get context about the field
                name = await input_field.get_attribute('name') or ''
                placeholder = await input_field.get_attribute('placeholder') or ''
                
                # Try to get label text
                parent = await input_field.query_selector('..')
                parent_text = ''
                if parent:
                    try:
                        parent_text = await parent.text_content() or ''
                    except:
                        pass
                
                combined = (name + placeholder + parent_text).lower()
                
                # Look for salary indicators
                if any(term in combined for term in ['salary', 'basic', 'annual', 'income']):
                    current_value = await input_field.input_value()
                    print(f"   Found salary field: {combined[:100]}")
                    print(f"   Current value: {current_value}")
                    
                    # Update the field
                    await input_field.clear()
                    await input_field.fill('40000')
                    await input_field.press('Tab')
                    print("   ✅ Updated salary to £40,000")
                    salary_updated = True
                    break
                    
            except Exception as e:
                print(f"   ⚠️ Error with input field: {e}")
                continue
        
        if salary_updated:
            await page.screenshot(path="after_salary_update.png")
        else:
            print("   ⚠️ No salary field found")
            
    except Exception as e:
        print(f"   ❌ Error updating salary: {e}")


async def click_get_results(page):
    """Look for and click Get Results button."""
    try:
        await page.screenshot(path="looking_for_results_button.png")
        
        # Look for buttons
        buttons = await page.query_selector_all('button, input[type="submit"]')
        
        for button in buttons:
            try:
                text = await button.text_content() or ''
                if any(term in text.lower() for term in ['get results', 'run', 'submit', 'calculate']):
                    print(f"   Found button: {text}")
                    await button.click()
                    await page.wait_for_load_state("networkidle", timeout=30000)
                    await page.wait_for_timeout(5000)
                    print("   ✅ Clicked results button")
                    
                    # Check for results
                    await page.screenshot(path="after_clicking_results.png")
                    page_text = await page.text_content('body')
                    
                    if any(term in page_text.lower() for term in ['results', 'lender', 'quote']):
                        print("🎉 RESULTS PAGE DETECTED!")
                        
                        # Look for target lenders
                        lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise"]
                        found = [l for l in lenders if l in page_text]
                        
                        if found:
                            print(f"🎉🎉🎉 LENDERS FOUND: {found} 🎉🎉🎉")
                            print("✅ EXISTING CASE APPROACH SUCCESSFUL!")
                        else:
                            print("✅ Results page reached")
                    else:
                        print("⚠️ Results not detected yet")
                    
                    return
                    
            except Exception as e:
                print(f"   ⚠️ Error with button: {e}")
                continue
        
        print("   ⚠️ No results button found")
        
    except Exception as e:
        print(f"   ❌ Error clicking results: {e}")


if __name__ == "__main__":
    asyncio.run(simple_case_test())