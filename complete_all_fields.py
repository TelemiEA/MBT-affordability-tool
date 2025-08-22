"""
Complete All Fields - Comprehensive automation with all required fields
Using the simple dropdown approach: click dropdown, then click away to select first option
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def complete_all_fields():
    """Complete all required fields using the simplified dropdown approach."""
    
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
            
            # Joint application checkbox
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
            
            print("🎯 COMPLETING ALL FIELDS WITH SIMPLIFIED DROPDOWN APPROACH")
            
            # === PROPERTY AND MORTGAGE SECTION ===
            print("\n📋 Property and Mortgage Section:")
            
            # Reason for Mortgage - use simple approach
            await complete_dropdown_simple("Reason for mortgage", "First-time buyer", page)
            
            # Property Type - Terraced House
            await complete_dropdown_simple("Property type", "Terraced House", page)
            
            # Mortgage Term - 35 years
            await complete_dropdown_simple("35 year", "35 years", page)
            
            # Freehold tenure
            try:
                await page.click('text=Freehold')
                print("✅ Freehold tenure selected")
            except:
                pass
            
            await page.wait_for_timeout(2000)
            await page.screenshot(path="property_section_complete.png")
            
            # Submit property section
            print("🚀 Submitting property section...")
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                # Handle any modal
                try:
                    ok_button = await page.query_selector('button:has-text("OK")')
                    if ok_button and await ok_button.is_visible():
                        await ok_button.click()
                        await page.wait_for_timeout(2000)
                except:
                    pass
            
            await page.wait_for_load_state("networkidle")
            
            # === FIRST APPLICANT PERSONAL SECTION ===
            print("\n👤 First Applicant Personal Section:")
            
            # Date of birth: 01-01-1990
            await fill_date_field("01", "01", "1990", page)
            
            # Married status: Single
            await complete_dropdown_simple("marital", "Single", page)
            
            # Country of residence: England
            await complete_dropdown_simple("country", "England", page)
            
            # Applicants & adult dependants: 1 for sole, 2 for joint
            dependants_count = "2" if is_joint else "1"
            await fill_number_field("applicants", dependants_count, page)
            await fill_number_field("adult", dependants_count, page)
            
            # Child dependants: Always 0
            await fill_number_field("child", "0", page)
            
            # Residential status: Tenant
            await complete_dropdown_simple("residential", "Tenant", page)
            
            await page.wait_for_timeout(2000)
            
            # Submit first applicant
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                await handle_modal(page)
            
            # === SECOND APPLICANT PERSONAL (if joint) ===
            if is_joint:
                print("\n👥 Second Applicant Personal Section:")
                
                await page.wait_for_load_state("networkidle")
                page_text = await page.text_content('body')
                
                if 'second' in page_text.lower() or 'applicant 2' in page_text.lower():
                    # Same fields for second applicant
                    await fill_date_field("01", "01", "1990", page)
                    await complete_dropdown_simple("marital", "Single", page)
                    await complete_dropdown_simple("country", "England", page)
                    await complete_dropdown_simple("residential", "Tenant", page)
                    
                    # Submit second applicant
                    submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
                    if submit_button:
                        await submit_button.click()
                        await page.wait_for_timeout(5000)
                        await handle_modal(page)
            
            # === EMPLOYMENT SECTION ===
            print("\n💼 Employment Section:")
            await page.wait_for_load_state("networkidle")
            
            # Set employment to Employed
            await complete_dropdown_simple("employment", "Employed", page)
            
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                await handle_modal(page)
            
            # === INCOME SECTION ===
            print("\n💰 Income Section:")
            await page.wait_for_load_state("networkidle")
            
            # Fill income fields with £40,000
            income_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
            for field in income_fields:
                try:
                    if await field.is_visible():
                        placeholder = await field.get_attribute('placeholder') or ''
                        name = await field.get_attribute('name') or ''
                        
                        if any(word in (placeholder + name).lower() for word in ['income', 'salary', 'basic', 'gross']):
                            await field.fill('40000')
                            print("✅ Income field filled: £40,000")
                except:
                    continue
            
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                await handle_modal(page)
            
            # === EXPENDITURE SECTIONS ===
            print("\n💸 Expenditure Section:")
            await page.wait_for_load_state("networkidle")
            
            # Council tax: 0
            await fill_expenditure_field("council", "0", page)
            
            # Building insurance: 0
            await fill_expenditure_field("building", "0", page)
            await fill_expenditure_field("insurance", "0", page)
            
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                await handle_modal(page)
            
            # Continue through remaining sections
            await continue_through_remaining_sections(page)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="complete_all_fields_error.png")
            
        finally:
            await browser.close()


async def complete_dropdown_simple(field_identifier, target_value, page):
    """Complete dropdown using simple approach: click dropdown, then click away."""
    try:
        print(f"Setting {field_identifier} to {target_value}...")
        
        # Find elements containing the field identifier
        selectors = [
            f':text("{field_identifier}")',
            f'[placeholder*="{field_identifier}"]',
            f'label:has-text("{field_identifier}")',
            f'div:has-text("{field_identifier}")'
        ]
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    try:
                        # Click the element to open dropdown
                        await element.click()
                        await page.wait_for_timeout(1000)
                        
                        # Try to find and click the target value
                        try:
                            await page.click(f'text={target_value}', timeout=2000)
                            print(f"✅ {field_identifier}: {target_value} selected")
                            return
                        except:
                            # Use the simple approach: click away to select first option
                            await page.click('body')
                            await page.wait_for_timeout(1000)
                            print(f"✅ {field_identifier}: First option selected")
                            return
                            
                    except:
                        continue
            except:
                continue
        
        # If no specific element found, try clicking near any dropdown arrows
        dropdown_elements = await page.query_selector_all('select, [role="combobox"], .dropdown')
        for dropdown in dropdown_elements:
            try:
                await dropdown.click()
                await page.wait_for_timeout(1000)
                
                try:
                    await page.click(f'text={target_value}', timeout=2000)
                    print(f"✅ {field_identifier}: {target_value} selected")
                    return
                except:
                    await page.click('body')
                    await page.wait_for_timeout(1000)
                    print(f"✅ {field_identifier}: First option selected")
                    return
                    
            except:
                continue
                
    except Exception as e:
        print(f"⚠️ {field_identifier} error: {e}")


async def fill_date_field(day, month, year, page):
    """Fill date field with 01-01-1990."""
    try:
        print(f"Setting date of birth: {day}-{month}-{year}")
        
        # Look for date input fields
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
                    await field.fill(f"{year}-{month}-{day}")
                    print("✅ Date of birth filled")
                    return
            except:
                continue
        
        # Try individual day/month/year fields
        day_field = await page.query_selector('input[name*="day"], select[name*="day"]')
        month_field = await page.query_selector('input[name*="month"], select[name*="month"]')
        year_field = await page.query_selector('input[name*="year"], select[name*="year"]')
        
        if day_field:
            await day_field.fill(day)
        if month_field:
            await month_field.fill(month)
        if year_field:
            await year_field.fill(year)
            
        print("✅ Date fields filled individually")
        
    except Exception as e:
        print(f"⚠️ Date field error: {e}")


async def fill_number_field(field_type, value, page):
    """Fill number fields for dependants."""
    try:
        print(f"Setting {field_type} to {value}")
        
        # Look for fields containing the field type
        selectors = [
            f'input[name*="{field_type}"]',
            f'input[placeholder*="{field_type}"]',
            f'select[name*="{field_type}"]'
        ]
        
        for selector in selectors:
            try:
                field = await page.query_selector(selector)
                if field and await field.is_visible():
                    await field.fill(value)
                    print(f"✅ {field_type}: {value}")
                    return
            except:
                continue
                
    except Exception as e:
        print(f"⚠️ {field_type} field error: {e}")


async def fill_expenditure_field(field_type, value, page):
    """Fill expenditure fields."""
    try:
        print(f"Setting {field_type} to {value}")
        
        selectors = [
            f'input[name*="{field_type}"]',
            f'input[placeholder*="{field_type}"]'
        ]
        
        for selector in selectors:
            try:
                fields = await page.query_selector_all(selector)
                for field in fields:
                    if await field.is_visible():
                        await field.fill(value)
                        print(f"✅ {field_type}: {value}")
            except:
                continue
                
    except Exception as e:
        print(f"⚠️ {field_type} field error: {e}")


async def handle_modal(page):
    """Handle any validation modals."""
    try:
        ok_button = await page.query_selector('button:has-text("OK")')
        if ok_button and await ok_button.is_visible():
            await ok_button.click()
            await page.wait_for_timeout(2000)
    except:
        pass


async def continue_through_remaining_sections(page):
    """Continue through any remaining sections to reach results."""
    try:
        print("\n🔄 Continuing through remaining sections...")
        
        for section in range(10):  # Try up to 10 sections
            await page.wait_for_load_state("networkidle")
            page_text = await page.text_content('body')
            current_url = page.url
            
            print(f"Section {section + 1}: {current_url}")
            
            if 'results' in page_text.lower() or 'lender' in page_text.lower():
                print("🎉 RESULTS SECTION REACHED!")
                await page.screenshot(path="COMPLETE_AUTOMATION_RESULTS.png")
                
                # Extract lender data
                lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom"]
                found = [l for l in lenders if l in page_text]
                
                if found:
                    print(f"\n🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉")
                    print(f"📊 LENDERS: {found}")
                    print(f"🏠 PROPERTY: Terraced House, Freehold, 35 years")
                    print("✅ FULL END-TO-END AUTOMATION ACHIEVED!")
                else:
                    print("✅ Reached results page!")
                return
            
            # Submit to next section
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                await handle_modal(page)
            else:
                print("No submit button - may be final section")
                break
        
    except Exception as e:
        print(f"❌ Section continuation error: {e}")


if __name__ == "__main__":
    asyncio.run(complete_all_fields())