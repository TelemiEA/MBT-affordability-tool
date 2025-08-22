"""
Step-by-step test to verify each part of the workflow works.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def test_step_by_step():
    """Test each step individually to identify issues."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            # Step 1: Login
            print("STEP 1: Login")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            if "signin" not in page.url.lower():
                print("✅ Login successful")
            else:
                print("❌ Login failed")
                return
            
            # Step 2: Create new case
            print("\nSTEP 2: Create new case")
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
            print(f"✅ New case created: {page.url}")
            
            # Step 3: Fill basic required fields
            print("\nSTEP 3: Fill basic required fields")
            await page.fill('input[name="firstname"]', 'Test')
            await page.fill('input[name="surname"]', 'User')
            await page.fill('input[name="email"]', 'test@example.com')
            print("✅ Basic fields filled")
            
            # Step 4: Set defaults
            print("\nSTEP 4: Set property and loan defaults")
            
            # Property value
            purchase_field = await page.query_selector('input[name="purchase"]')
            if purchase_field:
                await purchase_field.fill('1000000')
                print("✅ Property value set to £1,000,000")
            
            # Loan amount
            loan_field = await page.query_selector('input[name="loan_amount"]')
            if loan_field:
                await loan_field.fill('100000')
                print("✅ Loan amount set to £100,000")
            
            # Step 5: Set number of applicants
            print("\nSTEP 5: Set number of applicants to 2 (joint)")
            
            # Look for applicant dropdown
            applicant_selects = await page.query_selector_all('select')
            print(f"Found {len(applicant_selects)} select elements")
            
            # Try to find and set applicant number
            for i, select in enumerate(applicant_selects):
                name = await select.get_attribute('name')
                if name and 'applicant' in name.lower():
                    print(f"Found applicant select: {name}")
                    try:
                        await select.select_option('2')
                        print("✅ Set to 2 applicants")
                        await page.wait_for_timeout(2000)  # Wait for form update
                        break
                    except Exception as e:
                        print(f"Could not set applicant number: {e}")
            
            # Step 6: Set employment status
            print("\nSTEP 6: Set employment status to 'Employed'")
            
            # Look for employment dropdowns
            employment_selects = await page.query_selector_all('select')
            
            for i, select in enumerate(employment_selects):
                name = await select.get_attribute('name')
                if name and 'employment' in name.lower():
                    print(f"Found employment select: {name}")
                    
                    # Get available options
                    options = await select.query_selector_all('option')
                    option_texts = []
                    for option in options:
                        text = await option.text_content()
                        option_texts.append(text)
                    
                    print(f"Available options: {option_texts}")
                    
                    try:
                        await select.select_option('Employed')
                        print("✅ Set employment to Employed")
                        await page.wait_for_timeout(3000)  # Wait for income fields
                        break
                    except Exception as e:
                        print(f"Could not set employment: {e}")
            
            # Step 7: Check for income fields
            print("\nSTEP 7: Check for visible income fields")
            
            # Look for income-related fields
            all_inputs = await page.query_selector_all('input')
            income_fields = []
            
            for input_field in all_inputs:
                name = await input_field.get_attribute('name')
                if name and any(keyword in name.lower() for keyword in ['income', 'salary', 'basic']):
                    is_visible = await input_field.is_visible()
                    income_fields.append({
                        'name': name,
                        'visible': is_visible
                    })
            
            print("Income-related fields:")
            for field in income_fields:
                status = "✅ VISIBLE" if field['visible'] else "❌ HIDDEN"
                print(f"   {status}: {field['name']}")
            
            # Try to fill visible income fields
            print("\nSTEP 8: Fill visible income fields with £40,000")
            
            filled_count = 0
            for field_info in income_fields:
                if field_info['visible']:
                    try:
                        field = await page.query_selector(f'input[name="{field_info["name"]}"]')
                        if field:
                            await field.fill('40000')
                            print(f"✅ Filled {field_info['name']} with 40000")
                            filled_count += 1
                    except Exception as e:
                        print(f"❌ Could not fill {field_info['name']}: {e}")
            
            print(f"\nSUMMARY: Filled {filled_count} income fields")
            
            # Take final screenshot
            await page.screenshot(path="step_by_step_final.png")
            print("📸 Final screenshot saved: step_by_step_final.png")
            
            # Keep browser open for manual inspection
            print("\n⏳ Keeping browser open for 60 seconds for manual inspection...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="step_by_step_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_step_by_step())