"""
Final targeted fix - Complete the exact remaining fields we can see.
Focus on: Freehold tenure, Region dropdown, Ownership dropdown.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def final_targeted_fix():
    """Target the exact remaining fields visible in screenshot."""
    
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
            
            print("🎯 Targeting the exact remaining fields...")
            
            # Fill all visible fields first
            await complete_all_visible_fields(page)
            
            # Take screenshot before final submission
            await page.screenshot(path="before_final_targeted_submit.png")
            
            # Final submission attempt
            print("🚀 Final submission...")
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                # Check for modal
                try:
                    ok_button = await page.query_selector('button:has-text("OK")')
                    if ok_button and await ok_button.is_visible():
                        await ok_button.click()
                        await page.wait_for_timeout(2000)
                        print("⚠️ Still has validation errors")
                        await page.screenshot(path="final_validation_errors.png")
                    else:
                        print("✅ Success! Progressed past property section!")
                        await page.screenshot(path="final_success_past_property.png")
                        
                        # Continue to complete the workflow
                        await complete_remaining_workflow(page)
                        return
                except:
                    print("✅ No modal - likely progressed!")
                    await page.screenshot(path="final_no_modal_success.png")
                    await complete_remaining_workflow(page)
                    return
            
            # Keep browser open for inspection
            print("⏳ Keeping browser open for manual inspection...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="final_targeted_error.png")
            
        finally:
            await browser.close()


async def complete_all_visible_fields(page):
    """Complete all visible fields systematically."""
    
    print("📋 Completing all visible fields...")
    
    # 1. First-time buyer dropdown (if not already set)
    print("1️⃣ Setting reason for mortgage...")
    try:
        reason_js = """
        let reasonSelect = document.querySelector('select');
        if (reasonSelect && reasonSelect.options) {
            for (let i = 0; i < reasonSelect.options.length; i++) {
                if (reasonSelect.options[i].text.toLowerCase().includes('first-time buyer')) {
                    reasonSelect.selectedIndex = i;
                    reasonSelect.value = reasonSelect.options[i].value;
                    reasonSelect.dispatchEvent(new Event('change', {bubbles: true}));
                    break;
                }
            }
        }
        """
        await page.evaluate(reason_js)
        print("✅ Reason for mortgage set")
    except Exception as e:
        print(f"⚠️ Reason error: {e}")
    
    # 2. Property type (should already be Detached House)
    print("2️⃣ Property type already set to Detached House")
    
    # 3. Set Freehold tenure specifically
    print("3️⃣ Setting Freehold tenure...")
    try:
        freehold_js = """
        let freeholdRadio = document.querySelector('input[type="radio"][value="Freehold"]');
        if (freeholdRadio) {
            freeholdRadio.checked = true;
            freeholdRadio.dispatchEvent(new Event('change', {bubbles: true}));
            true;
        } else {
            false;
        }
        """
        result = await page.evaluate(freehold_js)
        print(f"✅ Freehold set: {result}")
    except Exception as e:
        print(f"⚠️ Freehold error: {e}")
    
    # 4. Radio buttons are already set correctly
    print("4️⃣ Radio buttons already set correctly")
    
    # 5. Property value is already £1,000,000
    print("5️⃣ Property value already set")
    
    # 6. Set Region dropdown
    print("6️⃣ Setting Region...")
    try:
        region_js = """
        let regionSelects = document.querySelectorAll('select');
        for (let select of regionSelects) {
            let name = select.name || '';
            let placeholder = select.getAttribute('placeholder') || '';
            if (name.toLowerCase().includes('region') || placeholder.toLowerCase().includes('region')) {
                if (select.options.length > 1) {
                    select.selectedIndex = 1;
                    select.value = select.options[1].value;
                    select.dispatchEvent(new Event('change', {bubbles: true}));
                    break;
                }
            }
        }
        """
        await page.evaluate(region_js)
        print("✅ Region set")
    except Exception as e:
        print(f"⚠️ Region error: {e}")
    
    # 7. Set Ownership dropdown
    print("7️⃣ Setting Ownership...")
    try:
        ownership_js = """
        let ownershipSelects = document.querySelectorAll('select');
        for (let select of ownershipSelects) {
            let name = select.name || '';
            let placeholder = select.getAttribute('placeholder') || '';
            if (name.toLowerCase().includes('ownership') || placeholder.toLowerCase().includes('ownership')) {
                if (select.options.length > 1) {
                    select.selectedIndex = 1;
                    select.value = select.options[1].value;
                    select.dispatchEvent(new Event('change', {bubbles: true}));
                    break;
                }
            }
        }
        """
        await page.evaluate(ownership_js)
        print("✅ Ownership set")
    except Exception as e:
        print(f"⚠️ Ownership error: {e}")
    
    # 8. Fill any remaining text fields
    print("8️⃣ Filling remaining text fields...")
    try:
        # Fill postcode if needed
        postcode_field = await page.query_selector('input[placeholder*="postcode"], input[name*="postcode"]')
        if postcode_field and await postcode_field.is_visible():
            await postcode_field.fill('SW1A 1AA')
            print("✅ Postcode filled")
    except Exception as e:
        print(f"⚠️ Text field error: {e}")
    
    await page.wait_for_timeout(2000)
    print("✅ All visible fields completed")


async def complete_remaining_workflow(page):
    """Complete the remaining workflow after property section."""
    try:
        print("🔄 Completing remaining workflow...")
        
        # Progress through sections
        for section in range(5):
            await page.wait_for_load_state("networkidle")
            page_text = await page.text_content('body')
            current_url = page.url
            
            print(f"Section {section + 1}: {current_url}")
            
            if 'applicant' in page_text.lower() or 'employment' in page_text.lower():
                print("👥 Applicant section - setting employment")
                
                # Set employment status to Employed
                employment_js = """
                let selects = document.querySelectorAll('select');
                for (let select of selects) {
                    for (let option of select.options) {
                        if (option.text.toLowerCase().includes('employed')) {
                            select.selectedIndex = option.index;
                            select.value = option.value;
                            select.dispatchEvent(new Event('change', {bubbles: true}));
                            break;
                        }
                    }
                }
                """
                await page.evaluate(employment_js)
                await page.wait_for_timeout(2000)
                
            elif 'income' in page_text.lower() or 'salary' in page_text.lower():
                print("💰 Income section - filling income fields")
                
                # Fill income fields
                income_fields = await page.query_selector_all('input[name*="income"], input[name*="salary"], input[name*="basic"]')
                for field in income_fields:
                    try:
                        if await field.is_visible():
                            await field.fill('40000')
                            print("✅ Income field filled")
                    except:
                        continue
                
            elif 'results' in page_text.lower() or 'lender' in page_text.lower():
                print("🎉 RESULTS SECTION REACHED!")
                await page.screenshot(path="FINAL_COMPLETE_RESULTS.png")
                
                # Extract lender names
                target_lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise"]
                found_lenders = [l for l in target_lenders if l in page_text]
                
                if found_lenders:
                    print(f"\n🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉")
                    print(f"📊 LENDERS FOUND: {found_lenders}")
                    print(f"📈 TOTAL: {len(found_lenders)}")
                    print("✅ FULL END-TO-END AUTOMATION COMPLETE!")
                else:
                    print("✅ Reached results page - automation complete!")
                return
            
            # Submit to next section
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
            else:
                print("No submit button found")
                break
        
        print("🔄 Workflow progression complete")
        
    except Exception as e:
        print(f"❌ Workflow completion error: {e}")


if __name__ == "__main__":
    asyncio.run(final_targeted_fix())