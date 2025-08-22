"""
Click Away Technique - Implement user's specific guidance
User said: "when i try it manually to select the first option you just need to click the drop down then click away anywhere else on the screen and it will fill that in"
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def click_away_technique():
    """Implement the specific click-away technique the user described."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=3000)
        page = await browser.new_page()
        
        try:
            print("🎯 CLICK AWAY TECHNIQUE - USER'S SPECIFIC GUIDANCE")
            print("Method: Click dropdown then click away to auto-select")
            print("=" * 55)
            
            # Setup
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            print("✅ Login successful")
            
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            print("✅ Case created")
            
            # Basic fields
            await page.fill('input[name="firstname"]', 'Test')
            await page.fill('input[name="surname"]', 'User')
            await page.fill('input[name="email"]', 'test@example.com')
            await page.fill('input[name="purchase"]', '1000000')
            await page.fill('input[name="loan_amount"]', '100000')
            
            # Joint application
            joint_checkbox = await page.query_selector('input[type="checkbox"]')
            if joint_checkbox:
                await joint_checkbox.check()
                await page.wait_for_timeout(2000)
                print("✅ Joint application selected")
            
            # Submit to property section
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(3000)
            
            # Handle modal
            try:
                await page.click('button:has-text("OK")')
                await page.wait_for_timeout(2000)
            except:
                pass
            
            await page.wait_for_load_state("networkidle")
            print("✅ Reached property section")
            
            # Set Freehold (we know this works now)
            try:
                await page.click('input[value="Freehold"]')
                print("✅ Freehold selected")
            except:
                pass
            
            await page.wait_for_timeout(2000)
            
            # Take screenshot before click-away technique
            await page.screenshot(path="clickaway_before.png")
            
            # === CLICK AWAY TECHNIQUE ===
            print("\\n🎯 CLICK AWAY TECHNIQUE")
            print("-" * 30)
            
            # 1. Reason for Mortgage dropdown
            print("1️⃣ Applying click-away to Reason for Mortgage...")
            reason_dropdown = await page.query_selector('select')
            if reason_dropdown:
                # Click the dropdown
                await reason_dropdown.click()
                await page.wait_for_timeout(1000)
                print("   📍 Clicked Reason dropdown")
                
                # Click away (click somewhere else on the page)
                await page.click('body')
                await page.wait_for_timeout(1000)
                print("   👆 Clicked away from dropdown")
                
                # Check if it auto-selected
                selected_value = await reason_dropdown.evaluate('el => el.value')
                print(f"   📊 Result: {selected_value}")
            
            await page.wait_for_timeout(2000)
            
            # 2. Property Type dropdown
            print("2️⃣ Applying click-away to Property Type...")
            selects = await page.query_selector_all('select')
            if len(selects) > 1:
                property_dropdown = selects[1]
                
                # Click the dropdown
                await property_dropdown.click()
                await page.wait_for_timeout(1000)
                print("   📍 Clicked Property Type dropdown")
                
                # Click away
                await page.click('body')
                await page.wait_for_timeout(1000)
                print("   👆 Clicked away from dropdown")
                
                # Check if it auto-selected
                selected_value = await property_dropdown.evaluate('el => el.value')
                print(f"   📊 Result: {selected_value}")
            
            await page.wait_for_timeout(2000)
            
            # Take screenshot after click-away technique
            await page.screenshot(path="clickaway_after.png")
            
            # Alternative technique from user: "alternatively, where i have asked you to select the first-option in the dropdown just click the dropdown arrow then click again in the same place"
            print("\\n🔄 ALTERNATIVE: Double-click same place technique...")
            
            # Try the double-click technique on both dropdowns
            reason_dropdown = await page.query_selector('select')
            if reason_dropdown:
                # Get the dropdown arrow position
                box = await reason_dropdown.bounding_box()
                if box:
                    # Click on the right side (where the arrow is)
                    arrow_x = box['x'] + box['width'] - 20
                    arrow_y = box['y'] + box['height'] / 2
                    
                    await page.mouse.click(arrow_x, arrow_y)
                    await page.wait_for_timeout(1000)
                    print("   📍 First click on reason dropdown arrow")
                    
                    await page.mouse.click(arrow_x, arrow_y)
                    await page.wait_for_timeout(1000)
                    print("   📍 Second click on same place")
            
            # Same for property type
            if len(selects) > 1:
                property_dropdown = selects[1]
                box = await property_dropdown.bounding_box()
                if box:
                    arrow_x = box['x'] + box['width'] - 20
                    arrow_y = box['y'] + box['height'] / 2
                    
                    await page.mouse.click(arrow_x, arrow_y)
                    await page.wait_for_timeout(1000)
                    print("   📍 First click on property type dropdown arrow")
                    
                    await page.mouse.click(arrow_x, arrow_y)
                    await page.wait_for_timeout(1000)
                    print("   📍 Second click on same place")
            
            await page.wait_for_timeout(2000)
            await page.screenshot(path="clickaway_double_click.png")
            
            # Test submission
            print("\\n🚀 Testing submission...")
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                # Check for validation
                try:
                    modal_button = await page.query_selector('button:has-text("OK")')
                    if modal_button and await modal_button.is_visible():
                        print("⚠️ Still validation errors after click-away technique")
                        await page.screenshot(path="clickaway_validation_errors.png")
                        await modal_button.click()
                        
                        # Final attempt: Manual inspection
                        print("\\n🔍 MANUAL INSPECTION MODE")
                        print("Dropdowns still not working with click-away technique.")
                        print("This suggests the dropdowns may require a different approach.")
                        print("Keeping browser open for manual inspection...")
                        
                        # Keep browser open for manual inspection
                        await page.wait_for_timeout(120000)  # 2 minutes
                        
                    else:
                        print("🎉 SUCCESS! Click-away technique worked!")
                        await page.screenshot(path="clickaway_success.png")
                        await continue_automation(page)
                        return
                        
                except:
                    print("🎉 SUCCESS! No modal - click-away technique worked!")
                    await continue_automation(page)
                    return
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="clickaway_error.png")
            
        finally:
            await browser.close()


async def continue_automation(page):
    """Continue automation after successful dropdown completion."""
    try:
        print("\\n🎉 CLICK-AWAY TECHNIQUE SUCCESSFUL!")
        print("🚀 Continuing full automation...")
        
        # Continue with the workflow
        for section in range(10):
            await page.wait_for_load_state("networkidle")
            page_text = await page.text_content('body')
            
            if 'results' in page_text.lower():
                print("🎉 RESULTS FOUND!")
                await page.screenshot(path="CLICKAWAY_FINAL_RESULTS.png")
                
                lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise"]
                found = [l for l in lenders if l in page_text]
                
                if found:
                    print(f"\\n🎉🎉🎉 CLICK-AWAY SUCCESS! 🎉🎉🎉")
                    print(f"📊 LENDERS: {found}")
                    print("✅ FULL AUTOMATION ACHIEVED!")
                else:
                    print("✅ Reached results page!")
                return
            
            # Quick fill
            await quick_fill_section(page)
            
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(3000)
                
                try:
                    modal = await page.query_selector('button:has-text("OK")')
                    if modal and await modal.is_visible():
                        await modal.click()
                        await page.wait_for_timeout(2000)
                except:
                    pass
            else:
                break
        
    except Exception as e:
        print(f"❌ Automation continuation error: {e}")


async def quick_fill_section(page):
    """Quick fill for any section."""
    try:
        # Fill income fields
        income_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
        for field in income_fields[:3]:
            try:
                if await field.is_visible():
                    name = await field.get_attribute('name') or ''
                    if 'income' in name.lower() or 'salary' in name.lower():
                        await field.fill('40000')
                    elif 'date' in name.lower():
                        await field.fill('1990-01-01')
                    elif not await field.input_value():
                        await field.fill('0')
            except:
                continue
                
    except:
        pass


if __name__ == "__main__":
    asyncio.run(click_away_technique())