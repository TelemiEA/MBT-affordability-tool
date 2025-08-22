#!/usr/bin/env python3
"""
Focused test to answer the key questions about MBT automation.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def focused_mbt_test():
    """Answer specific questions about MBT workflow."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            # Login
            print("🔐 Logging in...")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            print("✅ Logged in")
            
            # QUESTION 1: Create separate cases or reuse one case?
            print("\n🔍 QUESTION 1: Should we create separate cases for each scenario?")
            
            # Create first case
            print("📝 Creating FIRST case...")
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)
            
            # Get the case URL/ID
            first_case_url = page.url
            print(f"First case URL: {first_case_url}")
            
            # Fill minimal details for first scenario
            print("Filling Test Scenario 1: Joint £40k each")
            
            # Basic applicant info
            await page.fill('input[name="firstname"]', 'Test')
            await page.fill('input[name="surname"]', 'User1')
            await page.fill('input[name="email"]', 'test1@example.com')
            
            # Key insight: Let's see what happens when we submit this basic form
            print("\n🚀 Attempting to submit basic form...")
            submit_button = await page.query_selector('button[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(3000)
                
                # Check what page we're on now
                new_url = page.url
                print(f"After submit: {new_url}")
                
                # Look for validation errors to understand what's required
                error_elements = await page.query_selector_all('.error, .alert')
                required_fields = []
                
                for error in error_elements:
                    error_text = await error.text_content()
                    if error_text and 'please' in error_text.lower():
                        required_fields.append(error_text.strip())
                
                if required_fields:
                    print(f"\n📋 REQUIRED FIELDS IDENTIFIED:")
                    for i, field in enumerate(required_fields[:10]):  # Show first 10
                        print(f"   {i+1}. {field}")
                else:
                    print("✅ No validation errors - form may have been submitted")
            
            # Take screenshot of current state
            await page.screenshot(path="question1_first_case.png")
            print("📸 Screenshot: question1_first_case.png")
            
            # QUESTION 2: Input field verification
            print(f"\n🔍 QUESTION 2: Are we putting numbers in the RIGHT fields?")
            
            # Let's examine ALL input fields on the page
            all_inputs = await page.query_selector_all('input')
            income_related_fields = []
            
            print(f"Found {len(all_inputs)} total input fields")
            print("Looking for income/salary/amount related fields...")
            
            for i, input_field in enumerate(all_inputs):
                try:
                    name = await input_field.get_attribute('name')
                    placeholder = await input_field.get_attribute('placeholder') 
                    type_attr = await input_field.get_attribute('type')
                    
                    # Check if this looks like an income field
                    if name and any(keyword in name.lower() for keyword in ['income', 'salary', 'basic', 'amount', 'loan', 'purchase']):
                        is_visible = await input_field.is_visible()
                        income_related_fields.append({
                            'index': i,
                            'name': name,
                            'placeholder': placeholder,
                            'type': type_attr,
                            'visible': is_visible
                        })
                        
                except Exception as e:
                    continue
            
            print(f"\n💰 INCOME-RELATED FIELDS FOUND:")
            for field in income_related_fields:
                status = "✅ VISIBLE" if field['visible'] else "❌ HIDDEN"
                print(f"   {status} - name: '{field['name']}', placeholder: '{field['placeholder']}', type: '{field['type']}'")
            
            # QUESTION 3: Test actual input and verification
            print(f"\n🔍 QUESTION 3: Testing actual input values...")
            
            # Try to fill the most likely income fields
            test_income = 40000
            filled_fields = []
            
            for field_info in income_related_fields:
                if field_info['visible'] and field_info['type'] in ['text', 'number', None]:
                    try:
                        field = all_inputs[field_info['index']]
                        await field.fill(str(test_income))
                        
                        # Verify the value was actually set
                        value_after_fill = await field.input_value()
                        filled_fields.append({
                            'name': field_info['name'],
                            'filled_value': value_after_fill,
                            'success': value_after_fill == str(test_income)
                        })
                        
                        print(f"   Filled '{field_info['name']}' with {test_income}, got back: '{value_after_fill}'")
                        
                    except Exception as e:
                        print(f"   Failed to fill '{field_info['name']}': {e}")
            
            # Summary of filled fields
            print(f"\n📊 INPUT VERIFICATION SUMMARY:")
            successful_fills = [f for f in filled_fields if f['success']]
            print(f"   Successfully filled {len(successful_fills)} out of {len(filled_fields)} fields")
            
            for field in successful_fills:
                print(f"   ✅ {field['name']}: {field['filled_value']}")
            
            # Take screenshot after filling
            await page.screenshot(path="question3_after_filling.png")
            print("📸 Screenshot: question3_after_filling.png")
            
            # ANSWER to QUESTION 1: Test creating a second case
            print(f"\n🔍 TESTING: Creating a SECOND case...")
            
            # Navigate back to dashboard
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            
            # Create second case
            print("📝 Creating SECOND case...")
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)
            
            second_case_url = page.url
            print(f"Second case URL: {second_case_url}")
            
            # Compare URLs
            if first_case_url != second_case_url:
                print("✅ ANSWER 1: Each 'Create RESI Case' creates a SEPARATE case with unique URL")
                print("   RECOMMENDATION: Create separate cases for each scenario")
            else:
                print("❌ Same URL - may be reusing cases")
            
            print(f"\n🎯 KEY FINDINGS:")
            print(f"1. Cases: {'Separate' if first_case_url != second_case_url else 'Reused'}")
            print(f"2. Income fields found: {len(income_related_fields)}")
            print(f"3. Successfully filled: {len(successful_fills)} fields")
            print(f"4. Required validation fields: {len(required_fields)}")
            
            print(f"\n⏳ Keeping browser open for manual verification (30 seconds)...")
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="focused_test_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(focused_mbt_test())