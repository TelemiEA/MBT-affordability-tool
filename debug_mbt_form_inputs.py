#!/usr/bin/env python3
"""
Debug MBT form inputs to ensure we're filling the right fields with correct values.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def debug_form_inputs():
    """Debug form inputs step by step with manual verification."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            # Login first
            print("🔐 Logging in...")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            # Start new case
            print("📝 Starting new RESI case...")
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
            # Test Scenario: Joint application, both employed, £40k each
            print("\n🎯 Testing Joint Vanilla £40k scenario")
            print("Expected inputs:")
            print("- 2 applicants, both employed")
            print("- £40,000 income each") 
            print("- Property value: ~£320,000 (4x combined income)")
            print("- Loan amount: ~£256,000 (80% LTV)")
            
            # Fill basic applicant details
            print("\n👤 Filling applicant 1 details...")
            await page.fill('input[name="customer_title"]', 'Mr')
            await page.fill('input[name="firstname"]', 'John')
            await page.fill('input[name="surname"]', 'Smith')
            await page.fill('input[name="email"]', 'john.smith@test.com')
            await page.fill('input[name="customer_ref"]', 'TEST-JOINT-40K')
            
            # Select Residential (should be default)
            await page.check('input[name="type_of_quote"][value="Residential"]')
            
            # Select No for later life lending (should be default)
            await page.check('input[name="laterlife"][value="No"]')
            
            # Screenshot after basic details
            await page.screenshot(path="debug_step1_basic_details.png")
            print("📸 Screenshot: debug_step1_basic_details.png")
            
            # Mortgage preferences
            print("\n🏠 Setting mortgage preferences...")
            
            # Try to find and fill reason for mortgage
            print("Looking for 'Reason for mortgage' field...")
            reason_elements = await page.query_selector_all('input[placeholder*="reason" i], select[name*="reason" i]')
            print(f"Found {len(reason_elements)} reason-related elements")
            
            # Try the search input approach
            reason_search = await page.query_selector('input[placeholder="Reason for mortgage"]')
            if reason_search:
                print("Found reason search field, filling 'Purchase'...")
                await reason_search.fill('Purchase')
                await page.wait_for_timeout(1000)
                
                # Look for dropdown options
                dropdown_options = await page.query_selector_all('.ui-select-choices-row')
                if dropdown_options:
                    print(f"Found {len(dropdown_options)} dropdown options")
                    await dropdown_options[0].click()  # Select first option
                    print("Selected first dropdown option")
                else:
                    print("No dropdown options found")
            
            # Property details section
            print("\n🏡 Setting property details...")
            
            # Try to set property value
            property_value = 320000  # 4x combined income of £80k
            loan_amount = 256000     # 80% LTV
            
            print(f"Setting property value to £{property_value:,}")
            print(f"Setting loan amount to £{loan_amount:,}")
            
            # Look for property value fields
            property_fields = await page.query_selector_all('input[name*="purchase" i], input[name*="property" i], input[name*="value" i]')
            print(f"Found {len(property_fields)} property value fields")
            
            for i, field in enumerate(property_fields):
                name = await field.get_attribute('name')
                placeholder = await field.get_attribute('placeholder')
                print(f"  Field {i+1}: name='{name}', placeholder='{placeholder}'")
                
                if await field.is_visible():
                    print(f"  Filling field {i+1} with £{property_value}")
                    await field.fill(str(property_value))
                    break
            
            # Look for loan amount fields
            loan_fields = await page.query_selector_all('input[name*="loan" i], input[name*="advance" i], input[name*="amount" i]')
            print(f"Found {len(loan_fields)} loan amount fields")
            
            for i, field in enumerate(loan_fields):
                name = await field.get_attribute('name')
                placeholder = await field.get_attribute('placeholder')
                print(f"  Field {i+1}: name='{name}', placeholder='{placeholder}'")
                
                if await field.is_visible() and 'loan' in str(name).lower():
                    print(f"  Filling loan field {i+1} with £{loan_amount}")
                    await field.fill(str(loan_amount))
                    break
            
            # Screenshot after property details
            await page.screenshot(path="debug_step2_property_details.png")
            print("📸 Screenshot: debug_step2_property_details.png")
            
            # Income details - THIS IS CRITICAL
            print("\n💰 Setting income details...")
            
            # Look for income/salary fields
            income_fields = await page.query_selector_all('input[name*="salary" i], input[name*="income" i], input[name*="basic" i]')
            print(f"Found {len(income_fields)} income fields")
            
            applicant_income = 40000
            
            for i, field in enumerate(income_fields):
                name = await field.get_attribute('name')
                placeholder = await field.get_attribute('placeholder')
                print(f"  Income field {i+1}: name='{name}', placeholder='{placeholder}'")
                
                if await field.is_visible():
                    print(f"  Filling income field {i+1} with £{applicant_income}")
                    await field.fill(str(applicant_income))
                    # Only fill first two fields for joint application
                    if i >= 1:  # Stop after filling 2 fields
                        break
            
            # Employment status
            print("\n👔 Setting employment status...")
            employment_selects = await page.query_selector_all('select[name*="employment" i], select[name*="status" i]')
            print(f"Found {len(employment_selects)} employment dropdowns")
            
            for i, select in enumerate(employment_selects):
                if await select.is_visible():
                    name = await select.get_attribute('name')
                    print(f"  Setting employment dropdown {i+1} (name='{name}') to 'Employed'")
                    
                    # Try different option values
                    try:
                        await select.select_option('Employed')
                        print(f"  ✅ Selected 'Employed' in dropdown {i+1}")
                    except:
                        try:
                            await select.select_option('employed')
                            print(f"  ✅ Selected 'employed' in dropdown {i+1}")
                        except:
                            print(f"  ❌ Could not set employment in dropdown {i+1}")
                    
                    # Only set first two for joint application
                    if i >= 1:
                        break
            
            # Number of applicants
            print("\n👥 Setting number of applicants...")
            applicant_selects = await page.query_selector_all('select[name*="applicant" i]')
            
            for select in applicant_selects:
                if await select.is_visible():
                    print("Setting number of applicants to 2")
                    try:
                        await select.select_option('2')
                        print("✅ Set to 2 applicants")
                        break
                    except:
                        print("❌ Could not set number of applicants")
            
            # Screenshot after income details
            await page.screenshot(path="debug_step3_income_details.png")
            print("📸 Screenshot: debug_step3_income_details.png")
            
            # Now let's see what validation errors we get
            print("\n🚀 Attempting to submit and checking for errors...")
            
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(3000)
                
                # Check for validation errors
                error_elements = await page.query_selector_all('.error, .alert, [class*="error"]')
                if error_elements:
                    print(f"\n⚠️  Found {len(error_elements)} validation errors:")
                    for i, error in enumerate(error_elements[:10]):  # Show first 10
                        error_text = await error.text_content()
                        if error_text and error_text.strip():
                            print(f"  {i+1}. {error_text.strip()}")
                else:
                    print("✅ No validation errors found!")
                
                await page.screenshot(path="debug_step4_after_submit.png")
                print("📸 Screenshot: debug_step4_after_submit.png")
            
            # Check current page URL and content
            current_url = page.url
            print(f"\nCurrent URL: {current_url}")
            
            # Look for any results or next steps
            if "result" in current_url.lower() or "quote" in current_url.lower():
                print("🎯 Appears to be on results page!")
                
                # Look for lender results
                result_elements = await page.query_selector_all('table tr, .result, .lender')
                print(f"Found {len(result_elements)} potential result elements")
                
                # Try to extract some sample results
                for i, element in enumerate(result_elements[:5]):
                    text = await element.text_content()
                    if text and any(lender in text for lender in ['Accord', 'Skipton', 'Gen H']):
                        print(f"  Result {i+1}: {text[:100]}...")
            
            print("\n⏳ Keeping browser open for manual inspection (60 seconds)...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error during debug: {e}")
            await page.screenshot(path="debug_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_form_inputs())