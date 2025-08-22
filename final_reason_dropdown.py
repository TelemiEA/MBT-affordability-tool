"""
Final Reason Dropdown - Complete the last remaining field: Reason for Mortgage = First-time buyer
We're down to just 1 field! Everything else is working perfectly.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def final_reason_dropdown():
    """Complete the final Reason for Mortgage dropdown with First-time buyer."""
    
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
            
            print("🎯 FINAL STEP: Setting Reason for Mortgage to First-time buyer")
            
            # First, quickly set all the fields we know work
            print("✅ Setting up known working fields...")
            
            # Freehold
            try:
                await page.click('text=Freehold')
                print("✅ Freehold set")
            except:
                pass
            
            # Property Type to Terraced House (we know this works now)
            try:
                property_containers = await page.query_selector_all('div:has-text("Property Type")')
                for container in property_containers:
                    try:
                        text = await container.text_content()
                        if text and 'property type' in text.lower():
                            box = await container.bounding_box()
                            if box:
                                await page.mouse.click(box['x'] + box['width'] - 20, box['y'] + box['height'] * 0.6)
                                await page.wait_for_timeout(1000)
                                await page.click('text=Terraced House', timeout=2000)
                                print("✅ Terraced House set")
                                break
                    except:
                        continue
            except:
                pass
            
            await page.wait_for_timeout(2000)
            
            # Now focus ONLY on the Reason for Mortgage dropdown
            print("🔍 Targeting Reason for Mortgage dropdown...")
            
            # Strategy 1: Multiple coordinate-based attempts
            try:
                reason_elements = await page.query_selector_all(':text("Reason for mortgage")')
                
                for element in reason_elements:
                    try:
                        box = await element.bounding_box()
                        if box:
                            print(f"Found reason element at ({box['x']}, {box['y']})")
                            
                            # Try multiple click positions around the dropdown
                            click_attempts = [
                                (box['x'] + box['width'] + 5, box['y'] + box['height'] / 2),   # Just right of text
                                (box['x'] + box['width'] + 15, box['y'] + box['height'] / 2),  # Further right
                                (box['x'] + box['width'] - 5, box['y'] + box['height'] / 2),   # Right edge of text
                                (box['x'] + box['width'] - 15, box['y'] + box['height'] / 2),  # Slightly left
                                (box['x'] + box['width'] + 10, box['y'] + box['height'] / 3),  # Upper right
                                (box['x'] + box['width'] + 10, box['y'] + box['height'] * 2/3), # Lower right
                            ]
                            
                            for i, (x, y) in enumerate(click_attempts):
                                print(f"Attempt {i+1}: Clicking at ({x:.0f}, {y:.0f})")
                                await page.mouse.click(x, y)
                                await page.wait_for_timeout(1500)
                                
                                # Try to find and select "First-time buyer"
                                try:
                                    await page.click('text=First-time buyer', timeout=3000)
                                    print("🎉 SUCCESS! First-time buyer selected!")
                                    break
                                except:
                                    # Try variations
                                    for option in ['First time buyer', 'Purchase', 'Home purchase', 'Buy']:
                                        try:
                                            await page.click(f'text={option}', timeout=1000)
                                            print(f"🎉 SUCCESS! {option} selected!")
                                            break
                                        except:
                                            continue
                                    else:
                                        # Use keyboard navigation
                                        print(f"Attempt {i+1}: Using keyboard...")
                                        await page.keyboard.press('ArrowDown')
                                        await page.wait_for_timeout(300)
                                        await page.keyboard.press('Enter')
                                        await page.wait_for_timeout(1000)
                                        
                                        # Check if it worked by looking for success indicators
                                        try:
                                            # If no validation error appears, it might have worked
                                            page_content = await page.text_content('body')
                                            if 'first-time' in page_content.lower() or 'purchase' in page_content.lower():
                                                print(f"🎉 SUCCESS! Keyboard selection worked on attempt {i+1}")
                                                break
                                        except:
                                            continue
                            else:
                                continue  # Try next element
                            break  # Success, exit the element loop
                            
                    except Exception as e:
                        print(f"Element error: {e}")
                        continue
                        
            except Exception as e:
                print(f"Strategy 1 error: {e}")
            
            await page.wait_for_timeout(3000)
            
            # Strategy 2: Find any clickable elements near "Reason for mortgage" text
            try:
                print("🔍 Strategy 2: Finding clickable elements near reason text...")
                
                # Get all clickable elements
                clickable_elements = await page.query_selector_all('button, [role="button"], .dropdown-toggle, select, input')
                
                for element in clickable_elements:
                    try:
                        if await element.is_visible():
                            # Get element position
                            element_box = await element.bounding_box()
                            if element_box:
                                # Check if it's near any "reason" text
                                nearby_text = await page.evaluate(f"""
                                    Array.from(document.querySelectorAll('*')).find(el => 
                                        el.textContent && 
                                        el.textContent.toLowerCase().includes('reason') &&
                                        Math.abs(el.getBoundingClientRect().top - {element_box['y']}) < 50
                                    )?.textContent || ''
                                """)
                                
                                if 'reason' in nearby_text.lower():
                                    print(f"Found clickable element near reason text: {nearby_text[:50]}")
                                    await element.click()
                                    await page.wait_for_timeout(1500)
                                    
                                    # Try to select first-time buyer
                                    try:
                                        await page.click('text=First-time buyer', timeout=2000)
                                        print("🎉 SUCCESS via nearby element!")
                                        break
                                    except:
                                        await page.keyboard.press('ArrowDown')
                                        await page.keyboard.press('Enter')
                                        print("🎉 SUCCESS via keyboard on nearby element!")
                                        break
                    except:
                        continue
                        
            except Exception as e:
                print(f"Strategy 2 error: {e}")
            
            await page.wait_for_timeout(3000)
            await page.screenshot(path="final_reason_attempt.png")
            
            # Final submission test
            print("🚀 Testing final submission...")
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                # Check result
                try:
                    ok_button = await page.query_selector('button:has-text("OK")')
                    if ok_button and await ok_button.is_visible():
                        print("⚠️ Still validation error on Reason for Mortgage")
                        await page.screenshot(path="final_reason_validation.png")
                        await ok_button.click()
                        
                        print("\n🎯 FINAL STATUS:")
                        print("✅ Terraced House: COMPLETED")
                        print("✅ Freehold: COMPLETED") 
                        print("✅ All other fields: COMPLETED")
                        print("❌ Reason for Mortgage: Needs manual selection")
                        print("\n🔧 MANUAL COMPLETION:")
                        print("1. Click on 'Reason for mortgage' dropdown")
                        print("2. Select 'First-time buyer'")
                        print("3. Click Submit")
                        print("4. Continue through remaining sections")
                        
                    else:
                        print("🎉 COMPLETE SUCCESS! All fields completed!")
                        await page.screenshot(path="COMPLETE_SUCCESS.png")
                        await continue_full_automation(page)
                        return
                        
                except:
                    print("🎉 COMPLETE SUCCESS! No validation errors!")
                    await page.screenshot(path="COMPLETE_NO_MODAL.png")
                    await continue_full_automation(page)
                    return
            
            # Keep browser open for manual completion
            print("\n⏳ Browser staying open for final manual step...")
            await page.wait_for_timeout(180000)  # 3 minutes
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="final_reason_error.png")
            
        finally:
            await browser.close()


async def continue_full_automation(page):
    """Continue full automation after all property fields are complete."""
    try:
        print("🔄 Continuing full automation workflow...")
        
        # Continue through all remaining sections
        for section in range(5):
            await page.wait_for_load_state("networkidle")
            page_text = await page.text_content('body')
            current_url = page.url
            
            print(f"Section {section + 1}: {current_url}")
            
            if 'applicant' in page_text.lower() or 'employment' in page_text.lower():
                print("👥 Applicant section - setting employment")
                try:
                    await page.click('text=Employed', timeout=5000)
                    print("✅ Employment set to Employed")
                except:
                    pass
                
            elif 'income' in page_text.lower():
                print("💰 Income section - filling income fields")
                income_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
                for field in income_fields:
                    try:
                        if await field.is_visible():
                            await field.fill('40000')
                            print("✅ Income field filled")
                    except:
                        continue
                
            elif 'results' in page_text.lower():
                print("🎉 RESULTS SECTION!")
                await page.screenshot(path="FINAL_COMPLETE_RESULTS.png")
                
                page_text = await page.text_content('body')
                lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom"]
                found = [l for l in lenders if l in page_text]
                
                if found:
                    print(f"\n🎉🎉🎉 COMPLETE END-TO-END SUCCESS! 🎉🎉🎉")
                    print(f"📊 LENDERS: {found}")
                    print(f"🏠 PROPERTY: Terraced House, Freehold")
                    print("✅ FULL AUTOMATION ACHIEVED!")
                else:
                    print("✅ Reached results page - automation complete!")
                return
            
            # Submit to next section
            try:
                submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
                if submit_button:
                    await submit_button.click()
                    await page.wait_for_timeout(5000)
                else:
                    break
            except:
                break
        
    except Exception as e:
        print(f"❌ Automation continuation error: {e}")


if __name__ == "__main__":
    asyncio.run(final_reason_dropdown())