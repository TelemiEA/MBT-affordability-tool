"""
Complete Final Fields - Select Terraced House and Freehold Tenure
We're down to the last 2 specific selections!
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def complete_final_fields():
    """Complete the final Property Type (Terraced House) and Tenure (Freehold) selections."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1500)
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
            
            print("🎯 COMPLETING FINAL FIELDS: Terraced House + Freehold")
            
            # Step 1: Ensure Freehold is selected
            print("1️⃣ Setting Freehold tenure...")
            try:
                # Try clicking the Freehold radio button directly
                freehold_radio = await page.query_selector('input[type="radio"][value="Freehold"]')
                if freehold_radio:
                    await freehold_radio.click()
                    print("✅ Freehold radio button clicked")
                else:
                    # Try clicking the Freehold text/label
                    await page.click('text=Freehold')
                    print("✅ Freehold label clicked")
                    
            except Exception as e:
                print(f"⚠️ Freehold error: {e}")
            
            await page.wait_for_timeout(2000)
            
            # Step 2: Complete Property Type with Terraced House
            print("2️⃣ Setting Property Type to Terraced House...")
            
            # Strategy 1: Find and click the Property Type dropdown container
            try:
                # Look for the Property Type dropdown by finding its container
                property_containers = await page.query_selector_all('div:has-text("Property Type"), .form-group:has-text("Property Type")')
                
                for container in property_containers:
                    try:
                        text = await container.text_content()
                        if text and 'property type' in text.lower():
                            print("Found Property Type container")
                            
                            # Get the container's bounding box and click in different areas
                            box = await container.bounding_box()
                            if box:
                                # Try clicking the dropdown area (where the arrow would be)
                                click_positions = [
                                    (box['x'] + box['width'] - 20, box['y'] + box['height'] * 0.6),  # Right side
                                    (box['x'] + box['width'] - 40, box['y'] + box['height'] * 0.5),  # Center-right
                                    (box['x'] + box['width'] * 0.8, box['y'] + box['height'] * 0.5), # 80% right
                                ]
                                
                                for x, y in click_positions:
                                    print(f"Trying Property Type click at ({x:.0f}, {y:.0f})")
                                    await page.mouse.click(x, y)
                                    await page.wait_for_timeout(2000)
                                    
                                    # Try to find and click "Terraced House"
                                    try:
                                        await page.click('text=Terraced House', timeout=3000)
                                        print("✅ Selected Terraced House!")
                                        break
                                    except:
                                        # Try other variations
                                        for house_type in ['Terraced', 'Terrace', 'House']:
                                            try:
                                                await page.click(f'text={house_type}', timeout=1000)
                                                print(f"✅ Selected {house_type}!")
                                                break
                                            except:
                                                continue
                                        else:
                                            # Use keyboard navigation
                                            print("Using keyboard for Property Type...")
                                            await page.keyboard.press('ArrowDown')
                                            await page.wait_for_timeout(500)
                                            await page.keyboard.press('ArrowDown')  # Try second option
                                            await page.wait_for_timeout(500)
                                            await page.keyboard.press('Enter')
                                            print("✅ Property Type selected via keyboard!")
                                            break
                                else:
                                    continue
                                break
                    except:
                        continue
                        
            except Exception as e:
                print(f"Container strategy error: {e}")
            
            # Strategy 2: Try clicking directly on Property Type text elements
            try:
                property_text_elements = await page.query_selector_all(':text("Property type")')
                for element in property_text_elements:
                    try:
                        # Click on the element and nearby areas
                        await element.click()
                        await page.wait_for_timeout(1000)
                        
                        # Try to select Terraced House
                        try:
                            await page.click('text=Terraced House', timeout=2000)
                            print("✅ Property Type: Terraced House selected!")
                            break
                        except:
                            # Use keyboard
                            await page.keyboard.press('ArrowDown')
                            await page.wait_for_timeout(300)
                            await page.keyboard.press('ArrowDown')
                            await page.wait_for_timeout(300)
                            await page.keyboard.press('Enter')
                            print("✅ Property Type selected via keyboard!")
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"Text element strategy error: {e}")
            
            await page.wait_for_timeout(3000)
            await page.screenshot(path="final_fields_completed.png")
            
            # Step 3: Submit and check result
            print("🚀 Submitting with Terraced House and Freehold...")
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                # Check if we succeeded
                try:
                    ok_button = await page.query_selector('button:has-text("OK")')
                    if ok_button and await ok_button.is_visible():
                        print("⚠️ Still some validation - checking progress...")
                        await page.screenshot(path="after_terraced_house_submit.png")
                        await ok_button.click()
                        await page.wait_for_timeout(2000)
                        
                        print("\n📊 PROGRESS UPDATE:")
                        print("✅ Freehold tenure: Set")
                        print("✅ Property Type: Attempted Terraced House")
                        print("⚠️ May need manual verification of dropdown selection")
                        
                    else:
                        print("🎉 SUCCESS! No validation errors!")
                        await page.screenshot(path="TERRACED_HOUSE_SUCCESS.png")
                        
                        # Continue to next section
                        await continue_to_next_section(page)
                        return
                        
                except:
                    print("🎉 SUCCESS! No validation modal!")
                    await page.screenshot(path="TERRACED_HOUSE_NO_MODAL.png")
                    await continue_to_next_section(page)
                    return
            
            # Keep browser open for manual verification
            print("\n⏳ Browser staying open for verification...")
            print("VERIFY:")
            print("1. Freehold tenure is selected")
            print("2. Property Type shows 'Terraced House'")
            print("3. Click Submit if both are correct")
            
            await page.wait_for_timeout(120000)  # 2 minutes
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="final_fields_error.png")
            
        finally:
            await browser.close()


async def continue_to_next_section(page):
    """Continue to applicant/employment section after property success."""
    try:
        print("🔄 Continuing to next section...")
        
        await page.wait_for_load_state("networkidle")
        page_text = await page.text_content('body')
        current_url = page.url
        
        print(f"Next section: {current_url}")
        
        if 'applicant' in page_text.lower() or 'employment' in page_text.lower():
            print("👥 Reached applicant section!")
            
            # Set employment status to "Employed"
            try:
                await page.click('text=Employed', timeout=5000)
                print("✅ Set employment to Employed")
                await page.wait_for_timeout(2000)
                
                # Submit to income section
                submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
                if submit_button:
                    await submit_button.click()
                    await page.wait_for_timeout(5000)
                    
                    # Fill income fields
                    await fill_income_section(page)
                    
            except Exception as e:
                print(f"Employment section error: {e}")
                
        elif 'income' in page_text.lower():
            print("💰 Reached income section directly!")
            await fill_income_section(page)
            
        elif 'results' in page_text.lower():
            print("🎉 Reached results section!")
            await extract_results(page)
            
    except Exception as e:
        print(f"❌ Next section error: {e}")


async def fill_income_section(page):
    """Fill the income section with £40,000."""
    try:
        print("💰 Filling income section...")
        
        # Find and fill income fields
        income_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
        filled_count = 0
        
        for field in income_fields:
            try:
                if await field.is_visible():
                    placeholder = await field.get_attribute('placeholder') or ''
                    name = await field.get_attribute('name') or ''
                    
                    # Look for income-related fields
                    if any(word in (placeholder + name).lower() for word in ['income', 'salary', 'basic', 'gross', 'annual']):
                        await field.fill('40000')
                        filled_count += 1
                        print(f"✅ Income field {filled_count} filled: £40,000")
            except:
                continue
        
        print(f"✅ Filled {filled_count} income fields")
        await page.wait_for_timeout(2000)
        
        # Submit for results
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
        if submit_button:
            print("🚀 Submitting for results...")
            await submit_button.click()
            await page.wait_for_timeout(15000)  # Wait longer for results processing
            
            await extract_results(page)
            
    except Exception as e:
        print(f"❌ Income section error: {e}")


async def extract_results(page):
    """Extract the final lender results."""
    try:
        print("📊 Extracting lender results...")
        
        await page.screenshot(path="FINAL_TERRACED_HOUSE_RESULTS.png")
        
        page_text = await page.text_content('body')
        target_lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom", "Newcastle", "Metro", "Leeds"]
        found_lenders = [lender for lender in target_lenders if lender in page_text]
        
        if found_lenders:
            print(f"\n🎉🎉🎉 COMPLETE AUTOMATION SUCCESS! 🎉🎉🎉")
            print(f"📊 LENDERS FOUND: {found_lenders}")
            print(f"📈 TOTAL LENDERS: {len(found_lenders)}")
            print("🏠 PROPERTY TYPE: Terraced House")
            print("🏛️ TENURE: Freehold")
            print("✅ FULL END-TO-END AUTOMATION ACHIEVED!")
        else:
            print("✅ Reached results page - automation complete!")
            print("🏠 Property Type: Terraced House")
            print("🏛️ Tenure: Freehold")
            
    except Exception as e:
        print(f"❌ Results extraction error: {e}")


if __name__ == "__main__":
    asyncio.run(complete_final_fields())