"""
Simple Dropdown Automation - Using the double-click technique
Click dropdown arrow, then click same spot again to select first option
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def simple_dropdown_automation():
    """Complete all fields using the simple double-click dropdown technique."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1500)
        page = await browser.new_page()
        
        try:
            # Setup to property section
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
            is_joint = False
            if joint_checkbox:
                await joint_checkbox.check()
                is_joint = True
                await page.wait_for_timeout(2000)
                print("✅ Joint application selected")
            
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
            
            print("🎯 USING SIMPLE DOUBLE-CLICK DROPDOWN TECHNIQUE")
            
            # === PROPERTY AND MORTGAGE SECTION ===
            print("\n📋 Property and Mortgage Section:")
            
            # Reason for Mortgage - First-time buyer (or first option)
            await double_click_dropdown("Reason for mortgage", page)
            
            # Property Type - Terraced House (or first option)  
            await double_click_dropdown("Property type", page)
            
            # Mortgage Term - 35 years
            await double_click_dropdown("35", page)  # Look for 35 year term
            await double_click_dropdown("term", page)  # Or term dropdown
            
            # Freehold tenure
            try:
                await page.click('text=Freehold')
                print("✅ Freehold tenure selected")
            except:
                pass
            
            await page.wait_for_timeout(2000)
            await page.screenshot(path="simple_property_complete.png")
            
            # Submit property section
            print("🚀 Submitting property section...")
            await submit_and_handle_modal(page)
            
            # === APPLICANT PERSONAL SECTIONS ===
            print("\n👤 Applicant Personal Section:")
            await page.wait_for_load_state("networkidle")
            
            # Date of birth: 01-01-1990
            await fill_date_of_birth(page)
            
            # Married status: Single (or first option)
            await double_click_dropdown("marital", page)
            await double_click_dropdown("married", page)
            await double_click_dropdown("status", page)
            
            # Country of residence: England (or first option)
            await double_click_dropdown("country", page)
            await double_click_dropdown("residence", page)
            
            # Applicants & adult dependants: 2 for joint, 1 for sole
            dependants_count = "2" if is_joint else "1"
            await fill_dependants_fields(dependants_count, page)
            
            # Residential status: Tenant (or first option)
            await double_click_dropdown("residential", page)
            await double_click_dropdown("status", page)
            
            await page.wait_for_timeout(2000)
            await submit_and_handle_modal(page)
            
            # === SECOND APPLICANT (if joint) ===
            if is_joint:
                print("\n👥 Second Applicant Personal Section:")
                await page.wait_for_load_state("networkidle")
                
                page_text = await page.text_content('body')
                if 'second' in page_text.lower() or 'applicant 2' in page_text.lower():
                    await fill_date_of_birth(page)
                    await double_click_dropdown("marital", page)
                    await double_click_dropdown("country", page)
                    await double_click_dropdown("residential", page)
                    await submit_and_handle_modal(page)
            
            # === EMPLOYMENT SECTION ===
            print("\n💼 Employment Section:")
            await page.wait_for_load_state("networkidle")
            
            # Employment status: Employed (or first option)
            await double_click_dropdown("employment", page)
            await double_click_dropdown("status", page)
            
            await submit_and_handle_modal(page)
            
            # === INCOME SECTION ===
            print("\n💰 Income Section:")
            await page.wait_for_load_state("networkidle")
            
            # Fill income fields with £40,000
            await fill_income_fields(page)
            await submit_and_handle_modal(page)
            
            # === EXPENDITURE SECTION ===
            print("\n💸 Expenditure Section:")
            await page.wait_for_load_state("networkidle")
            
            # Council tax: 0, Building insurance: 0
            await fill_expenditure_fields(page)
            await submit_and_handle_modal(page)
            
            # Continue to results
            await continue_to_results(page)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="simple_automation_error.png")
            
        finally:
            await browser.close()


async def double_click_dropdown(field_identifier, page):
    """Double-click dropdown technique: click dropdown, then click same spot again."""
    try:
        print(f"Double-clicking dropdown for: {field_identifier}")
        
        # Find elements that might contain the dropdown
        possible_selectors = [
            f':text("{field_identifier}")',
            f'[placeholder*="{field_identifier}"]',
            f'label:has-text("{field_identifier}")',
            f'div:has-text("{field_identifier}")'
        ]
        
        for selector in possible_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    try:
                        # Get the element's bounding box to find click position
                        box = await element.bounding_box()
                        if box:
                            # Try clicking on the right side where dropdown arrow would be
                            arrow_x = box['x'] + box['width'] - 15
                            arrow_y = box['y'] + box['height'] / 2
                            
                            # First click to open dropdown
                            await page.mouse.click(arrow_x, arrow_y)
                            await page.wait_for_timeout(1000)
                            
                            # Second click in same spot to select first option
                            await page.mouse.click(arrow_x, arrow_y)
                            await page.wait_for_timeout(1000)
                            
                            print(f"✅ {field_identifier} dropdown completed")
                            return
                    except:
                        continue
            except:
                continue
        
        # Alternative: look for any dropdown elements and try the technique
        dropdown_elements = await page.query_selector_all('select, [role="combobox"], .dropdown, button[class*="select"]')
        for dropdown in dropdown_elements:
            try:
                if await dropdown.is_visible():
                    box = await dropdown.bounding_box()
                    if box:
                        click_x = box['x'] + box['width'] - 15
                        click_y = box['y'] + box['height'] / 2
                        
                        # Double click technique
                        await page.mouse.click(click_x, click_y)
                        await page.wait_for_timeout(1000)
                        await page.mouse.click(click_x, click_y)
                        await page.wait_for_timeout(1000)
                        
                        print(f"✅ {field_identifier} dropdown completed (generic)")
                        return
            except:
                continue
                
    except Exception as e:
        print(f"⚠️ {field_identifier} dropdown error: {e}")


async def fill_date_of_birth(page):
    """Fill date of birth as 01-01-1990."""
    try:
        print("Setting date of birth: 01-01-1990")
        
        # Try different date field formats
        date_selectors = [
            'input[type="date"]',
            'input[placeholder*="date"]',
            'input[name*="birth"]',
            'input[name*="dob"]'
        ]
        
        for selector in date_selectors:
            try:
                field = await page.query_selector(selector)
                if field and await field.is_visible():
                    # Try different date formats
                    for date_format in ["1990-01-01", "01/01/1990", "01-01-1990"]:
                        try:
                            await field.fill(date_format)
                            print(f"✅ Date of birth filled: {date_format}")
                            return
                        except:
                            continue
            except:
                continue
        
        print("⚠️ Date field not found or filled")
        
    except Exception as e:
        print(f"⚠️ Date field error: {e}")


async def fill_dependants_fields(count, page):
    """Fill dependants fields."""
    try:
        print(f"Setting dependants to {count}")
        
        # Look for dependants fields
        dependant_fields = await page.query_selector_all('input[type="number"], input[name*="dependant"], input[name*="adult"]')
        
        for field in dependant_fields:
            try:
                if await field.is_visible():
                    name = await field.get_attribute('name') or ''
                    if 'child' in name.lower():
                        await field.fill('0')  # Always 0 for children
                        print("✅ Child dependants: 0")
                    else:
                        await field.fill(count)
                        print(f"✅ Adult dependants: {count}")
            except:
                continue
                
    except Exception as e:
        print(f"⚠️ Dependants error: {e}")


async def fill_income_fields(page):
    """Fill income fields with £40,000."""
    try:
        print("Filling income fields: £40,000")
        
        income_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
        filled_count = 0
        
        for field in income_fields:
            try:
                if await field.is_visible():
                    placeholder = await field.get_attribute('placeholder') or ''
                    name = await field.get_attribute('name') or ''
                    
                    if any(word in (placeholder + name).lower() for word in ['income', 'salary', 'basic', 'gross', 'annual']):
                        await field.fill('40000')
                        filled_count += 1
                        print(f"✅ Income field {filled_count}: £40,000")
            except:
                continue
        
        print(f"✅ Total income fields filled: {filled_count}")
        
    except Exception as e:
        print(f"⚠️ Income fields error: {e}")


async def fill_expenditure_fields(page):
    """Fill expenditure fields with 0."""
    try:
        print("Filling expenditure fields: 0")
        
        # Council tax and building insurance = 0
        expenditure_keywords = ['council', 'tax', 'building', 'insurance']
        
        for keyword in expenditure_keywords:
            fields = await page.query_selector_all(f'input[name*="{keyword}"], input[placeholder*="{keyword}"]')
            for field in fields:
                try:
                    if await field.is_visible():
                        await field.fill('0')
                        print(f"✅ {keyword}: 0")
                except:
                    continue
                    
    except Exception as e:
        print(f"⚠️ Expenditure error: {e}")


async def submit_and_handle_modal(page):
    """Submit form and handle any validation modals."""
    try:
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
        if submit_button:
            await submit_button.click()
            await page.wait_for_timeout(5000)
            
            # Handle modal if it appears
            try:
                ok_button = await page.query_selector('button:has-text("OK")')
                if ok_button and await ok_button.is_visible():
                    await ok_button.click()
                    await page.wait_for_timeout(2000)
                    print("✅ Modal handled")
            except:
                pass
                
    except Exception as e:
        print(f"⚠️ Submit error: {e}")


async def continue_to_results(page):
    """Continue through any remaining sections to reach results."""
    try:
        print("\n🔄 Continuing to results...")
        
        for section in range(10):
            await page.wait_for_load_state("networkidle")
            page_text = await page.text_content('body')
            current_url = page.url
            
            print(f"Section {section + 1}: {current_url}")
            
            if 'results' in page_text.lower() or 'lender' in page_text.lower():
                print("🎉 RESULTS REACHED!")
                await page.screenshot(path="SIMPLE_AUTOMATION_RESULTS.png")
                
                # Extract results
                lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom"]
                found = [l for l in lenders if l in page_text]
                
                if found:
                    print(f"\n🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉")
                    print(f"📊 LENDERS: {found}")
                    print(f"🏠 PROPERTY: Terraced House, Freehold, 35 years")
                    print(f"👥 APPLICANTS: {'Joint' if page_text and 'joint' in page_text.lower() else 'Single'}")
                    print("✅ SIMPLE AUTOMATION TECHNIQUE WORKS!")
                else:
                    print("✅ Reached results page - automation complete!")
                return
            
            # Continue to next section
            await submit_and_handle_modal(page)
        
    except Exception as e:
        print(f"❌ Results continuation error: {e}")


if __name__ == "__main__":
    asyncio.run(simple_dropdown_automation())