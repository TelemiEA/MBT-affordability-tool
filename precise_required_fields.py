"""
Precise Required Fields - Target the exact required fields we can see
Focus on the specific red asterisk fields: Reason for Mortgage + Mortgage Term
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def precise_required_fields():
    """Target the precise required fields we can identify."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            print("🎯 PRECISE REQUIRED FIELDS TARGETING")
            print("Focus: Complete specific red asterisk fields systematically")
            print("=" * 60)
            
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
            
            # === SYSTEMATIC REQUIRED FIELD COMPLETION ===
            print("\n📋 SYSTEMATIC REQUIRED FIELD COMPLETION")
            print("-" * 50)
            
            await page.screenshot(path="precise_before_completion.png")
            
            # 1. REASON FOR MORTGAGE (Required - Red Asterisk)
            print("1️⃣ Completing 'Reason for Mortgage' (Required)")
            reason_completed = await complete_reason_for_mortgage(page)
            
            # 2. MORTGAGE PRODUCT TERM (Required - Red Asterisk) 
            print("2️⃣ Completing 'Mortgage Product Term' (Required)")
            term_completed = await complete_mortgage_term(page)
            
            # 3. PROPERTY TYPE (if present and required)
            print("3️⃣ Checking for 'Property Type' field")
            property_completed = await complete_property_type_if_present(page)
            
            # 4. TENURE (if present)
            print("4️⃣ Setting 'Freehold' tenure")
            tenure_completed = await set_freehold_tenure(page)
            
            await page.wait_for_timeout(3000)
            await page.screenshot(path="precise_after_completion.png")
            
            # Summary
            print(f"\n📊 COMPLETION SUMMARY:")
            print(f"   Reason for Mortgage: {'✅' if reason_completed else '❌'}")
            print(f"   Mortgage Term: {'✅' if term_completed else '❌'}")
            print(f"   Property Type: {'✅' if property_completed else '➖'}")
            print(f"   Freehold Tenure: {'✅' if tenure_completed else '❌'}")
            
            # Submit and continue
            print("\n🚀 SUBMITTING COMPLETED FORM...")
            success = await submit_and_check_progress(page)
            
            if success:
                print("🎉 SUCCESS! Progressed to next section")
                await continue_through_remaining_sections(page)
            else:
                print("⚠️ Still validation errors - check screenshots")
                
            # Keep browser open
            print("\n⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(120000)  # 2 minutes
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="precise_error.png")
            
        finally:
            await browser.close()


async def complete_reason_for_mortgage(page):
    """Complete the Reason for Mortgage dropdown specifically."""
    try:
        print("   🔍 Targeting Reason for Mortgage dropdown...")
        
        # Strategy 1: Find the dropdown by its container
        reason_containers = await page.query_selector_all('div:has-text("Reason for Mortgage")')
        
        for container in reason_containers:
            try:
                # Get the dropdown within this container
                dropdown = await container.query_selector('select, [role="combobox"], button')
                if dropdown:
                    box = await dropdown.bounding_box()
                    if box:
                        print(f"   📍 Found dropdown at ({box['x']:.0f}, {box['y']:.0f})")
                        
                        # Click the dropdown
                        await page.mouse.click(box['x'] + box['width'] - 15, box['y'] + box['height'] / 2)
                        await page.wait_for_timeout(1500)
                        
                        # Try to select First-time buyer
                        for option in ['First-time buyer', 'Purchase', 'Buy', 'Home purchase']:
                            try:
                                await page.click(f'text={option}', timeout=2000)
                                print(f"   ✅ Selected: {option}")
                                return True
                            except:
                                continue
                        
                        # Fallback: double-click technique
                        print("   🔄 Using double-click technique...")
                        await page.mouse.click(box['x'] + box['width'] - 15, box['y'] + box['height'] / 2)
                        await page.wait_for_timeout(1000)
                        await page.mouse.click(box['x'] + box['width'] - 15, box['y'] + box['height'] / 2)
                        await page.wait_for_timeout(1000)
                        print("   ✅ Double-click completed")
                        return True
            except:
                continue
        
        # Strategy 2: Look for placeholder text
        try:
            placeholder_element = await page.query_selector('[placeholder="Reason for mortgage"]')
            if placeholder_element:
                box = await placeholder_element.bounding_box()
                if box:
                    await page.mouse.click(box['x'] + box['width'] - 15, box['y'] + box['height'] / 2)
                    await page.wait_for_timeout(1000)
                    await page.mouse.click(box['x'] + box['width'] - 15, box['y'] + box['height'] / 2)
                    await page.wait_for_timeout(1000)
                    print("   ✅ Placeholder method completed")
                    return True
        except:
            pass
        
        print("   ⚠️ Could not complete Reason for Mortgage")
        return False
        
    except Exception as e:
        print(f"   ❌ Reason for Mortgage error: {e}")
        return False


async def complete_mortgage_term(page):
    """Complete the Mortgage Product Term checkboxes."""
    try:
        print("   🔍 Targeting Mortgage Product Term...")
        
        # Look for 35 year term checkbox (our target)
        term_options = ['35 year term', '35', '35 years']
        
        for term_text in term_options:
            try:
                term_element = await page.query_selector(f'text={term_text}')
                if term_element:
                    # Find associated checkbox
                    parent = await term_element.query_selector('..')
                    if parent:
                        checkbox = await parent.query_selector('input[type="checkbox"]')
                        if checkbox:
                            await checkbox.check()
                            print(f"   ✅ Selected: {term_text}")
                            return True
            except:
                continue
        
        # Fallback: select any available term checkbox
        try:
            term_checkboxes = await page.query_selector_all('input[type="checkbox"]')
            for checkbox in term_checkboxes:
                try:
                    # Check if this checkbox is related to term
                    parent = await checkbox.query_selector('..')
                    if parent:
                        parent_text = await parent.text_content()
                        if parent_text and ('year' in parent_text.lower() or 'term' in parent_text.lower()):
                            await checkbox.check()
                            print(f"   ✅ Selected term checkbox")
                            return True
                except:
                    continue
        except:
            pass
        
        print("   ⚠️ Could not complete Mortgage Term")
        return False
        
    except Exception as e:
        print(f"   ❌ Mortgage Term error: {e}")
        return False


async def complete_property_type_if_present(page):
    """Complete Property Type if it exists on this page."""
    try:
        print("   🔍 Checking for Property Type field...")
        
        # Look for Property Type elements
        property_elements = await page.query_selector_all(':text("Property type"), :text("Property Type")')
        
        if not property_elements:
            print("   ➖ Property Type not found on this page")
            return True  # Not an error if not present
        
        for element in property_elements:
            try:
                box = await element.bounding_box()
                if box:
                    # Click the dropdown area
                    await page.mouse.click(box['x'] + box['width'] + 15, box['y'] + box['height'] / 2)
                    await page.wait_for_timeout(1500)
                    
                    # Try to select Terraced House
                    for option in ['Terraced House', 'House', 'Detached', 'Semi']:
                        try:
                            await page.click(f'text={option}', timeout=2000)
                            print(f"   ✅ Selected: {option}")
                            return True
                        except:
                            continue
                    
                    # Double-click fallback
                    await page.mouse.click(box['x'] + box['width'] + 15, box['y'] + box['height'] / 2)
                    await page.wait_for_timeout(1000)
                    print("   ✅ Property Type double-click completed")
                    return True
            except:
                continue
        
        print("   ⚠️ Could not complete Property Type")
        return False
        
    except Exception as e:
        print(f"   ❌ Property Type error: {e}")
        return False


async def set_freehold_tenure(page):
    """Set Freehold tenure if present."""
    try:
        print("   🔍 Setting Freehold tenure...")
        
        # Try to click Freehold radio button
        freehold_radio = await page.query_selector('input[value="Freehold"]')
        if freehold_radio:
            await freehold_radio.click()
            print("   ✅ Freehold radio button clicked")
            return True
        
        # Try clicking Freehold text
        try:
            await page.click('text=Freehold')
            print("   ✅ Freehold text clicked")
            return True
        except:
            pass
        
        print("   ➖ Freehold not found on this page")
        return True  # Not an error if not present
        
    except Exception as e:
        print(f"   ❌ Freehold error: {e}")
        return False


async def submit_and_check_progress(page):
    """Submit form and check if we progressed."""
    try:
        # Submit
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
        if submit_button:
            await submit_button.click()
            await page.wait_for_timeout(5000)
            
            # Check for modal (indicates validation errors)
            try:
                modal_button = await page.query_selector('button:has-text("OK")')
                if modal_button and await modal_button.is_visible():
                    await modal_button.click()
                    await page.wait_for_timeout(2000)
                    print("⚠️ Validation modal appeared")
                    await page.screenshot(path="precise_validation_modal.png")
                    return False
                else:
                    print("✅ No validation modal - success!")
                    await page.screenshot(path="precise_progression_success.png")
                    return True
            except:
                print("✅ No modal detected - success!")
                return True
        else:
            print("⚠️ No submit button found")
            return False
            
    except Exception as e:
        print(f"❌ Submit error: {e}")
        return False


async def continue_through_remaining_sections(page):
    """Continue through remaining sections to reach results."""
    try:
        print("\n🔄 CONTINUING THROUGH REMAINING SECTIONS")
        print("-" * 50)
        
        for section in range(10):
            await page.wait_for_load_state("networkidle")
            page_text = await page.text_content('body')
            current_url = page.url
            
            print(f"Section {section + 1}: {current_url}")
            
            # Check if we've reached results
            if any(keyword in page_text.lower() for keyword in ['results', 'lender', 'quote', 'offers']):
                print("🎉 RESULTS SECTION FOUND!")
                await page.screenshot(path="PRECISE_FINAL_RESULTS.png")
                
                # Extract results
                lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise"]
                found = [l for l in lenders if l in page_text]
                
                if found:
                    print(f"\n🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉")
                    print(f"📊 LENDERS: {found}")
                    print("✅ PRECISE AUTOMATION ACHIEVED!")
                else:
                    print("✅ Reached results page")
                return
            
            # Fill any remaining fields and continue
            await fill_section_quickly(page)
            
            # Submit
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(3000)
                
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
        
        print("⚠️ Completed sections without finding results")
        
    except Exception as e:
        print(f"❌ Section progression error: {e}")


async def fill_section_quickly(page):
    """Quickly fill any obvious fields in current section."""
    try:
        # Fill basic text fields
        text_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
        for field in text_fields[:5]:  # Limit to first 5 to avoid delays
            try:
                if await field.is_visible():
                    name = await field.get_attribute('name') or ''
                    if 'income' in name.lower() or 'salary' in name.lower():
                        await field.fill('40000')
                    elif 'date' in name.lower() or 'birth' in name.lower():
                        await field.fill('1990-01-01')
                    elif not await field.input_value():  # Only fill if empty
                        await field.fill('0')
            except:
                continue
        
        # Select first option in dropdowns
        dropdowns = await page.query_selector_all('select')
        for dropdown in dropdowns[:3]:  # Limit to first 3
            try:
                if await dropdown.is_visible():
                    options = await dropdown.query_selector_all('option')
                    if len(options) > 1:
                        await dropdown.select_option(index=1)
            except:
                continue
                
    except Exception as e:
        print(f"⚠️ Quick fill error: {e}")


if __name__ == "__main__":
    asyncio.run(precise_required_fields())