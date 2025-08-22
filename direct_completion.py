"""
Direct completion of the specific dropdowns we can see in the screenshot.
This will use a simple, direct approach to complete the exact fields.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def direct_complete():
    """Directly complete the form to get to results."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1500)
        page = await browser.new_page()
        
        try:
            # Login
            print("🔐 Login...")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            # Create case
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
            # Basic fields 
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
                        print(f"✅ {selector}")
                except:
                    pass
            
            # Joint application
            joint_checkbox = await page.query_selector('input[type="checkbox"]')
            if joint_checkbox:
                await joint_checkbox.check()
                print("✅ Joint application")
                await page.wait_for_timeout(2000)
            
            # Submit to property section
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(3000)
                
                # Dismiss modal
                try:
                    ok_button = await page.query_selector('button:has-text("OK")')
                    if ok_button and await ok_button.is_visible():
                        await ok_button.click()
                        await page.wait_for_timeout(2000)
                except:
                    pass
                
                await page.wait_for_load_state("networkidle")
            
            print("🎯 Now at property section - using manual approach...")
            
            # Take screenshot
            await page.screenshot(path="direct_property_section.png")
            
            # Manual step-by-step approach
            print("Step 1: Click on Reason for Mortgage dropdown")
            
            # Use a more targeted approach - scroll to dropdown first
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(1000)
            
            # Look for dropdown by its container
            try:
                # Try to click the dropdown area
                await page.click('text=Reason for mortgage', timeout=5000)
                await page.wait_for_timeout(1000)
                print("✅ Clicked reason dropdown text")
            except:
                try:
                    # Try clicking the dropdown container
                    await page.click('[placeholder="Reason for mortgage"]')
                    await page.wait_for_timeout(1000)
                    print("✅ Clicked reason dropdown placeholder")
                except:
                    print("⚠️ Could not click reason dropdown")
            
            # Try using keyboard navigation
            print("Step 2: Using keyboard to select options")
            try:
                # Tab through form elements
                await page.keyboard.press('Tab')
                await page.wait_for_timeout(500)
                await page.keyboard.press('Tab')
                await page.wait_for_timeout(500)
                await page.keyboard.press('Tab')
                await page.wait_for_timeout(500)
                
                # When we hit a dropdown, open it
                await page.keyboard.press('Space')
                await page.wait_for_timeout(1000)
                
                # Select first option
                await page.keyboard.press('ArrowDown')
                await page.wait_for_timeout(500)
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(1000)
                
                print("✅ Used keyboard navigation")
            except Exception as e:
                print(f"⚠️ Keyboard navigation failed: {e}")
            
            # Use JavaScript to force-fill dropdowns
            print("Step 3: Using JavaScript to force-complete")
            
            js_code = """
            // Find all dropdowns and complete them
            const selects = document.querySelectorAll('select');
            let completed = 0;
            
            selects.forEach((select, index) => {
                if (select.options.length > 1) {
                    select.selectedIndex = 1;
                    select.value = select.options[1].value;
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                    console.log('Set dropdown', index, 'to', select.options[1].text);
                    completed++;
                }
            });
            
            // Also try to click radio buttons
            const radios = document.querySelectorAll('input[type="radio"]');
            radios.forEach(radio => {
                if (radio.value === 'Freehold' || radio.value === 'Yes' || radio.value === 'No') {
                    if (!radio.checked) {
                        radio.checked = true;
                        radio.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            });
            
            return { completed: completed, totalSelects: selects.length };
            """
            
            js_result = await page.evaluate(js_code)
            print(f"JavaScript result: {js_result}")
            
            # Wait and take screenshot
            await page.wait_for_timeout(3000)
            await page.screenshot(path="after_js_completion.png")
            
            # Multiple submission attempts
            for attempt in range(3):
                print(f"\\nSubmission attempt {attempt + 1}")
                
                # Try submitting
                submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
                if submit_button:
                    await submit_button.click()
                    await page.wait_for_timeout(5000)
                    
                    # Handle any modals
                    try:
                        ok_button = await page.query_selector('button:has-text("OK")')
                        if ok_button and await ok_button.is_visible():
                            await ok_button.click()
                            await page.wait_for_timeout(2000)
                            print("⚠️ Modal appeared - still have validation")
                            
                            # Try the JavaScript completion again
                            await page.evaluate(js_code)
                            await page.wait_for_timeout(2000)
                        else:
                            print("✅ No modal - likely progressed!")
                            break
                    except:
                        print("✅ No modal detected")
                        break
                    
                    await page.wait_for_load_state("networkidle")
                else:
                    print("❌ No submit button")
                    break
            
            # Take final screenshot and check results
            await page.screenshot(path="final_direct_result.png")
            
            # Check current state
            current_url = page.url
            page_text = await page.text_content('body')
            
            print(f"\\nFinal URL: {current_url}")
            
            # Look for success indicators
            if 'results' in page_text.lower() or 'lender' in page_text.lower():
                print("🎉 SUCCESS! Found results page!")
                
                # Try to extract some results
                lender_names = ['Gen H', 'Accord', 'Skipton', 'Kensington']
                found_lenders = []
                
                for lender in lender_names:
                    if lender in page_text:
                        found_lenders.append(lender)
                
                if found_lenders:
                    print(f"🎉 Found lenders: {found_lenders}")
                else:
                    print("⚠️ On results page but no target lenders found")
                    
            elif 'applicant' in page_text.lower() or 'employment' in page_text.lower():
                print("✅ Progressed to applicant section!")
                
                # Look for income fields
                income_fields = await page.query_selector_all('input[name*="income"], input[name*="salary"]')
                print(f"Found {len(income_fields)} income fields")
                
                if len(income_fields) > 0:
                    print("✅ Ready for income field completion!")
                    
            elif 'please' in page_text.lower():
                print("❌ Still have validation errors")
            else:
                print("⚠️ Unknown state")
            
            # Keep browser open
            print("\\n⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="direct_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(direct_complete())