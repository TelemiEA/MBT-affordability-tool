"""
Final targeted fix for the last 2 dropdowns: Reason for Mortgage and Property Type.
Based on the exact screenshot showing these specific validation errors.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def complete_final_dropdowns():
    """Complete the final 2 dropdowns to unlock the next section."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            # Quick setup to get to the exact section we need
            print("🔐 Quick setup...")
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
            
            # Quick progression to the section
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
                except:
                    pass
            
            # Joint application
            joint_checkbox = await page.query_selector('input[type="checkbox"]')
            if joint_checkbox:
                await joint_checkbox.check()
                await page.wait_for_timeout(2000)
            
            # Submit to get to dropdown section
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                # Dismiss any modals
                try:
                    ok_button = await page.query_selector('button:has-text("OK")')
                    if ok_button and await ok_button.is_visible():
                        await ok_button.click()
                        await page.wait_for_timeout(2000)
                except:
                    pass
                
                await page.wait_for_load_state("networkidle")
            
            # Now we should be at the section with the 2 problematic dropdowns
            print("🎯 Targeting the specific problematic dropdowns...")
            
            # Take screenshot to confirm location
            await page.screenshot(path="final_target_location.png")
            
            # Method 1: Direct selection by looking for dropdowns with validation errors
            print("📋 Method 1: Finding dropdowns by validation context...")
            
            # Look for elements with validation error text
            reason_error = await page.query_selector('text=Please choose reason for mortgage')
            if reason_error:
                print("✅ Found 'reason for mortgage' error text")
                # Find the associated dropdown
                reason_dropdown = await page.query_selector('select')
                if reason_dropdown:
                    print("🎯 Found reason dropdown near error text")
                    
                    # Get all options
                    options = await reason_dropdown.query_selector_all('option')
                    option_texts = []
                    for option in options:
                        text = await option.text_content()
                        value = await option.get_attribute('value')
                        option_texts.append(f"'{text}' = {value}")
                    
                    print(f"Reason options: {option_texts}")
                    
                    # Try different purchase-related options
                    success = False
                    for option in ['Purchase', 'purchase', 'Purchase of property', 'Buy', 'Home purchase', '1', '2', '3']:
                        try:
                            await reason_dropdown.select_option(option)
                            print(f"✅ SUCCESS: Set reason to '{option}'")
                            success = True
                            await page.wait_for_timeout(2000)
                            break
                        except Exception as e:
                            print(f"⚠️ Failed to set '{option}': {e}")
                            continue
                    
                    if not success and len(options) > 1:
                        # Try selecting by index
                        for i in range(1, min(4, len(options))):
                            try:
                                await reason_dropdown.select_option(index=i)
                                selected_value = await reason_dropdown.input_value()
                                print(f"✅ Set reason to index {i}: '{selected_value}'")
                                success = True
                                break
                            except:
                                continue
            
            # Wait and check for property type dropdown
            await page.wait_for_timeout(2000)
            
            property_error = await page.query_selector('text=Please select property type')
            if property_error:
                print("✅ Found 'property type' error text")
                
                # Look for the property type dropdown
                # It might be the second select element
                all_selects = await page.query_selector_all('select')
                print(f"Found {len(all_selects)} total select elements")
                
                for i, select in enumerate(all_selects):
                    try:
                        # Skip the first one (likely reason dropdown)
                        if i == 0:
                            continue
                            
                        print(f"🎯 Trying select element {i+1} for property type...")
                        
                        options = await select.query_selector_all('option')
                        option_texts = []
                        for option in options:
                            text = await option.text_content()
                            value = await option.get_attribute('value')
                            option_texts.append(f"'{text}' = {value}")
                        
                        print(f"Options for select {i+1}: {option_texts}")
                        
                        # Try property-related options
                        success = False
                        for option in ['House', 'house', 'Detached', 'detached', 'Semi-detached', 'Flat', 'Apartment', '1', '2', '3']:
                            try:
                                await select.select_option(option)
                                print(f"✅ SUCCESS: Set property type to '{option}'")
                                success = True
                                await page.wait_for_timeout(2000)
                                break
                            except Exception as e:
                                print(f"⚠️ Failed to set '{option}': {e}")
                                continue
                        
                        if success:
                            break
                        elif len(options) > 1:
                            # Try by index
                            for idx in range(1, min(4, len(options))):
                                try:
                                    await select.select_option(index=idx)
                                    selected_value = await select.input_value()
                                    print(f"✅ Set property type to index {idx}: '{selected_value}'")
                                    success = True
                                    break
                                except:
                                    continue
                        
                        if success:
                            break
                            
                    except Exception as e:
                        print(f"⚠️ Error with select {i+1}: {e}")
                        continue
            
            # Take screenshot after dropdown attempts
            await page.screenshot(path="after_final_dropdown_attempts.png")
            
            # Final submit attempt
            print("🚀 Final submit attempt...")
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                # Handle modals
                try:
                    ok_button = await page.query_selector('button:has-text("OK")')
                    if ok_button and await ok_button.is_visible():
                        await ok_button.click()
                        await page.wait_for_timeout(2000)
                        print("⚠️ Modal appeared - might still have validation errors")
                    else:
                        print("✅ No modal - likely successful!")
                except:
                    pass
                
                await page.wait_for_load_state("networkidle")
                
                # Take final screenshot
                await page.screenshot(path="final_result_state.png")
                
                # Check current state
                page_text = await page.text_content('body')
                current_url = page.url
                
                print(f"Current URL: {current_url}")
                
                # Check for success indicators
                if 'please choose' not in page_text.lower() and 'please select' not in page_text.lower():
                    print("🎉 SUCCESS! No more 'please choose/select' validation errors!")
                    
                    # Look for applicant/income section indicators
                    success_indicators = ['applicant', 'employment', 'income', 'salary', 'personal details']
                    found_indicators = [indicator for indicator in success_indicators if indicator in page_text.lower()]
                    
                    if found_indicators:
                        print(f"🎉 MAJOR SUCCESS! Found next section indicators: {found_indicators}")
                        
                        # Check for visible income fields
                        income_fields = await page.query_selector_all('input[name*="income"], input[name*="salary"], input[name*="net_profit"]')
                        visible_income = 0
                        for field in income_fields:
                            if await field.is_visible():
                                visible_income += 1
                        
                        if visible_income > 0:
                            print(f"🎉 BREAKTHROUGH! Found {visible_income} VISIBLE income fields!")
                        else:
                            print(f"Found {len(income_fields)} income fields (not yet visible)")
                    else:
                        print("⚠️ Progressed but not yet at applicant section")
                else:
                    print("❌ Still have validation errors")
                    
                    # Show remaining errors
                    if 'please choose' in page_text.lower():
                        print("   - Still need to choose reason for mortgage")
                    if 'please select' in page_text.lower():
                        print("   - Still need to select property type")
            
            # Keep browser open
            print("⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="final_completion_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(complete_final_dropdowns())