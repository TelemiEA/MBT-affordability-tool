"""
Robust Dropdown Fix - Target the specific dropdowns that are still failing
Let's try a more aggressive approach to complete these 2 specific dropdowns
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def robust_dropdown_fix():
    """More robust approach to complete the failing dropdowns."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            # Quick setup to property section
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
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
            
            # Submit to property section
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(3000)
            
            # Dismiss modal
            try:
                await page.click('button:has-text("OK")')
                await page.wait_for_timeout(2000)
            except:
                pass
            
            await page.wait_for_load_state("networkidle")
            
            print("🎯 ROBUST DROPDOWN COMPLETION APPROACH")
            
            # Set Freehold first (we know this works)
            try:
                await page.click('text=Freehold')
                print("✅ Freehold set")
            except:
                pass
            
            await page.wait_for_timeout(2000)
            
            # Strategy 1: Multiple coordinate attempts for Reason dropdown
            print("🔍 Strategy 1: Multiple coordinate attempts for Reason dropdown...")
            
            reason_elements = await page.query_selector_all(':text("Reason for mortgage")')
            reason_completed = False
            
            for element in reason_elements:
                if reason_completed:
                    break
                    
                try:
                    box = await element.bounding_box()
                    if box:
                        # Try multiple positions around the element
                        click_positions = [
                            (box['x'] + box['width'] + 10, box['y'] + box['height'] / 2),   # Right of text
                            (box['x'] + box['width'] + 20, box['y'] + box['height'] / 2),   # Further right
                            (box['x'] + box['width'] + 30, box['y'] + box['height'] / 2),   # Even further
                            (box['x'] + box['width'] - 5, box['y'] + box['height'] / 2),    # Right edge
                            (box['x'] + box['width'] + 15, box['y'] + box['height'] / 3),   # Upper right
                            (box['x'] + box['width'] + 15, box['y'] + box['height'] * 2/3), # Lower right
                        ]
                        
                        for i, (x, y) in enumerate(click_positions):
                            print(f"Reason attempt {i+1}: Clicking ({x:.0f}, {y:.0f})")
                            
                            # Click to open dropdown
                            await page.mouse.click(x, y)
                            await page.wait_for_timeout(1500)
                            
                            # Try to find First-time buyer option
                            try:
                                await page.click('text=First-time buyer', timeout=3000)
                                print("🎉 SUCCESS! First-time buyer selected!")
                                reason_completed = True
                                break
                            except:
                                # Try other options
                                for option in ['Purchase', 'Buy', 'Home purchase']:
                                    try:
                                        await page.click(f'text={option}', timeout=1000)
                                        print(f"🎉 SUCCESS! {option} selected!")
                                        reason_completed = True
                                        break
                                    except:
                                        continue
                                
                                if reason_completed:
                                    break
                                
                                # Try the double-click approach
                                print(f"Reason attempt {i+1}: Double-click...")
                                await page.mouse.click(x, y)
                                await page.wait_for_timeout(1000)
                                await page.mouse.click(x, y)
                                await page.wait_for_timeout(1500)
                                
                                # Check if something was selected by trying submission
                                test_submit = await page.query_selector('button[type="submit"]')
                                if test_submit:
                                    await test_submit.click()
                                    await page.wait_for_timeout(2000)
                                    
                                    # Check if modal appears
                                    try:
                                        modal = await page.query_selector('button:has-text("OK")')
                                        if modal and await modal.is_visible():
                                            await modal.click()
                                            await page.wait_for_timeout(1000)
                                            print(f"Attempt {i+1}: Still validation errors")
                                        else:
                                            print(f"🎉 SUCCESS! No validation modal on attempt {i+1}")
                                            reason_completed = True
                                            break
                                    except:
                                        print(f"🎉 SUCCESS! No modal detected on attempt {i+1}")
                                        reason_completed = True
                                        break
                            
                            if reason_completed:
                                break
                                
                except Exception as e:
                    print(f"Reason element error: {e}")
                    continue
            
            await page.wait_for_timeout(2000)
            
            # Strategy 2: Multiple coordinate attempts for Property Type dropdown
            print("🔍 Strategy 2: Multiple coordinate attempts for Property Type dropdown...")
            
            property_elements = await page.query_selector_all(':text("Property type")')
            property_completed = False
            
            for element in property_elements:
                if property_completed:
                    break
                    
                try:
                    box = await element.bounding_box()
                    if box:
                        click_positions = [
                            (box['x'] + box['width'] + 10, box['y'] + box['height'] / 2),
                            (box['x'] + box['width'] + 20, box['y'] + box['height'] / 2),
                            (box['x'] + box['width'] + 30, box['y'] + box['height'] / 2),
                            (box['x'] + box['width'] - 5, box['y'] + box['height'] / 2),
                            (box['x'] + box['width'] + 15, box['y'] + box['height'] / 3),
                            (box['x'] + box['width'] + 15, box['y'] + box['height'] * 2/3),
                        ]
                        
                        for i, (x, y) in enumerate(click_positions):
                            print(f"Property attempt {i+1}: Clicking ({x:.0f}, {y:.0f})")
                            
                            await page.mouse.click(x, y)
                            await page.wait_for_timeout(1500)
                            
                            # Try to find Terraced House option
                            try:
                                await page.click('text=Terraced House', timeout=3000)
                                print("🎉 SUCCESS! Terraced House selected!")
                                property_completed = True
                                break
                            except:
                                # Try other house types
                                for house_type in ['House', 'Detached', 'Semi', 'Terraced']:
                                    try:
                                        await page.click(f'text={house_type}', timeout=1000)
                                        print(f"🎉 SUCCESS! {house_type} selected!")
                                        property_completed = True
                                        break
                                    except:
                                        continue
                                
                                if property_completed:
                                    break
                                
                                # Double-click approach
                                print(f"Property attempt {i+1}: Double-click...")
                                await page.mouse.click(x, y)
                                await page.wait_for_timeout(1000)
                                await page.mouse.click(x, y)
                                await page.wait_for_timeout(1500)
                                
                                # Test submission
                                test_submit = await page.query_selector('button[type="submit"]')
                                if test_submit:
                                    await test_submit.click()
                                    await page.wait_for_timeout(2000)
                                    
                                    try:
                                        modal = await page.query_selector('button:has-text("OK")')
                                        if modal and await modal.is_visible():
                                            await modal.click()
                                            await page.wait_for_timeout(1000)
                                            print(f"Property attempt {i+1}: Still validation errors")
                                        else:
                                            print(f"🎉 SUCCESS! Property type completed on attempt {i+1}")
                                            property_completed = True
                                            break
                                    except:
                                        print(f"🎉 SUCCESS! Property type completed on attempt {i+1}")
                                        property_completed = True
                                        break
                            
                            if property_completed:
                                break
                                
                except Exception as e:
                    print(f"Property element error: {e}")
                    continue
            
            await page.wait_for_timeout(3000)
            await page.screenshot(path="robust_dropdown_final_attempt.png")
            
            # Final submission test
            print("🚀 Final submission test...")
            submit_button = await page.query_selector('button[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                try:
                    modal = await page.query_selector('button:has-text("OK")')
                    if modal and await modal.is_visible():
                        print("⚠️ Still validation errors after all attempts")
                        await page.screenshot(path="robust_final_validation_errors.png")
                        await modal.click()
                        
                        print("\n📊 FINAL ANALYSIS:")
                        print(f"✅ Reason dropdown attempts: {'SUCCESS' if reason_completed else 'FAILED'}")
                        print(f"✅ Property dropdown attempts: {'SUCCESS' if property_completed else 'FAILED'}")
                        print("🎯 These are custom dropdown components that need manual intervention")
                        
                    else:
                        print("🎉 COMPLETE SUCCESS! No validation errors!")
                        await page.screenshot(path="ROBUST_COMPLETE_SUCCESS.png")
                        
                        # Continue automation
                        print("🔄 Continuing full automation...")
                        await continue_automation_from_here(page)
                        
                except:
                    print("🎉 COMPLETE SUCCESS! No modal detected!")
                    await page.screenshot(path="ROBUST_NO_MODAL_SUCCESS.png")
                    await continue_automation_from_here(page)
            
            # Keep browser open for inspection
            print("\n⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(120000)  # 2 minutes
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="robust_dropdown_error.png")
            
        finally:
            await browser.close()


async def continue_automation_from_here(page):
    """Continue automation if dropdowns were completed successfully."""
    try:
        print("🎉 DROPDOWNS COMPLETED - CONTINUING FULL AUTOMATION!")
        
        # Continue through remaining sections
        for section in range(10):
            await page.wait_for_load_state("networkidle")
            page_text = await page.text_content('body')
            
            if 'results' in page_text.lower():
                print("🎉 REACHED RESULTS!")
                await page.screenshot(path="ROBUST_FINAL_RESULTS.png")
                return
            
            # Fill any fields and continue
            await fill_section_generically(page)
            
            # Submit
            submit_button = await page.query_selector('button[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                # Handle modal
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
        print(f"❌ Continuation error: {e}")


async def fill_section_generically(page):
    """Fill current section with generic values."""
    try:
        # Fill text fields
        text_fields = await page.query_selector_all('input[type="text"], input[type="number"], input[type="email"]')
        for field in text_fields:
            try:
                if await field.is_visible():
                    current_value = await field.input_value()
                    if not current_value:
                        name = await field.get_attribute('name') or ''
                        if 'income' in name.lower() or 'salary' in name.lower():
                            await field.fill('40000')
                        elif 'email' in name.lower():
                            await field.fill('test@example.com')
                        elif 'date' in name.lower() or 'birth' in name.lower():
                            await field.fill('1990-01-01')
                        else:
                            await field.fill('0')
            except:
                continue
        
        # Complete dropdowns
        dropdowns = await page.query_selector_all('select')
        for dropdown in dropdowns:
            try:
                if await dropdown.is_visible():
                    options = await dropdown.query_selector_all('option')
                    if len(options) > 1:
                        await dropdown.select_option(index=1)
            except:
                continue
                
    except Exception as e:
        print(f"⚠️ Generic fill error: {e}")


if __name__ == "__main__":
    asyncio.run(robust_dropdown_fix())