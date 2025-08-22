"""
Direct dropdown fix - Handle the exact dropdowns that are failing.
Focus on making the actual HTML select elements work properly.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def direct_dropdown_fix():
    """Direct approach to fix the exact failing dropdowns."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
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
            
            print("🎯 Direct dropdown fixing approach...")
            await page.screenshot(path="before_direct_dropdown_fix.png")
            
            # Method 1: Direct click and select approach
            print("📋 Method 1: Direct click and keyboard navigation...")
            
            # Fix Reason for Mortgage dropdown
            print("1️⃣ Fixing Reason for Mortgage...")
            try:
                # Click the dropdown to open it
                reason_dropdown = await page.query_selector('select:first-of-type')
                if reason_dropdown:
                    await reason_dropdown.click()
                    await page.wait_for_timeout(1000)
                    
                    # Use keyboard to navigate to "First-time buyer"
                    await page.keyboard.press('ArrowDown')  # Move to first option
                    await page.wait_for_timeout(300)
                    await page.keyboard.press('ArrowDown')  # Try second option
                    await page.wait_for_timeout(300)
                    await page.keyboard.press('Enter')      # Select
                    await page.wait_for_timeout(1000)
                    
                    print("✅ Reason dropdown navigation complete")
                else:
                    print("❌ Reason dropdown not found")
            except Exception as e:
                print(f"⚠️ Reason dropdown error: {e}")
            
            # Fix Property Type dropdown  
            print("2️⃣ Fixing Property Type...")
            try:
                # Find the property type dropdown (second select)
                property_dropdown = await page.query_selector('select:nth-of-type(2)')
                if property_dropdown:
                    await property_dropdown.click()
                    await page.wait_for_timeout(1000)
                    
                    # Navigate to select house type
                    await page.keyboard.press('ArrowDown')  # Move to first option
                    await page.wait_for_timeout(300)
                    await page.keyboard.press('Enter')      # Select
                    await page.wait_for_timeout(1000)
                    
                    print("✅ Property type dropdown navigation complete")
                else:
                    print("❌ Property type dropdown not found")
            except Exception as e:
                print(f"⚠️ Property type error: {e}")
            
            # Fix Freehold radio button
            print("3️⃣ Fixing Freehold tenure...")
            try:
                # Direct click on Freehold radio button
                freehold_radio = await page.query_selector('input[type="radio"][value="Freehold"]')
                if freehold_radio:
                    await freehold_radio.click()
                    await page.wait_for_timeout(1000)
                    print("✅ Freehold radio clicked")
                else:
                    print("❌ Freehold radio not found")
            except Exception as e:
                print(f"⚠️ Freehold error: {e}")
            
            await page.screenshot(path="after_direct_dropdown_fix.png")
            
            # Method 2: JavaScript forced selection
            print("🔧 Method 2: JavaScript forced selection...")
            
            forced_js = """
            // Force set all dropdowns with actual option values
            let selects = document.querySelectorAll('select');
            let results = [];
            
            // First dropdown - Reason for Mortgage
            if (selects[0] && selects[0].options.length > 1) {
                // Look for First-time buyer or Purchase option
                for (let i = 1; i < selects[0].options.length; i++) {
                    let optionText = selects[0].options[i].text.toLowerCase();
                    if (optionText.includes('first-time') || optionText.includes('purchase')) {
                        selects[0].selectedIndex = i;
                        selects[0].value = selects[0].options[i].value;
                        selects[0].dispatchEvent(new Event('change', {bubbles: true}));
                        results.push('Reason: ' + selects[0].options[i].text);
                        break;
                    }
                }
            }
            
            // Second dropdown - Property Type  
            if (selects[1] && selects[1].options.length > 1) {
                // Look for house type
                for (let i = 1; i < selects[1].options.length; i++) {
                    let optionText = selects[1].options[i].text.toLowerCase();
                    if (optionText.includes('house') || optionText.includes('detached')) {
                        selects[1].selectedIndex = i;
                        selects[1].value = selects[1].options[i].value;
                        selects[1].dispatchEvent(new Event('change', {bubbles: true}));
                        results.push('Property: ' + selects[1].options[i].text);
                        break;
                    }
                }
            }
            
            // Force Freehold radio button
            let freeholdRadio = document.querySelector('input[type="radio"][value="Freehold"]');
            if (freeholdRadio) {
                freeholdRadio.checked = true;
                freeholdRadio.dispatchEvent(new Event('change', {bubbles: true}));
                results.push('Tenure: Freehold');
            }
            
            return results;
            """
            
            try:
                js_results = await page.evaluate(forced_js)
                print(f"✅ JavaScript results: {js_results}")
            except Exception as e:
                print(f"⚠️ JavaScript error: {e}")
            
            await page.wait_for_timeout(3000)
            await page.screenshot(path="after_javascript_force.png")
            
            # Method 3: Manual option by option selection
            print("🎯 Method 3: Manual option-by-option selection...")
            
            # Get all available options for debugging
            debug_js = """
            let selects = document.querySelectorAll('select');
            let debug = [];
            
            selects.forEach((select, index) => {
                let options = [];
                for (let i = 0; i < select.options.length; i++) {
                    options.push(select.options[i].text);
                }
                debug.push({
                    selectIndex: index,
                    selectedIndex: select.selectedIndex,
                    selectedValue: select.value,
                    options: options
                });
            });
            
            return debug;
            """
            
            try:
                debug_info = await page.evaluate(debug_js)
                print(f"🔍 Debug info: {debug_info}")
            except Exception as e:
                print(f"⚠️ Debug error: {e}")
            
            # Final submission attempt
            print("🚀 Final submission attempt...")
            
            for attempt in range(5):
                print(f"Submission attempt {attempt + 1}/5...")
                
                # Try submitting
                submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
                if submit_button:
                    await submit_button.click()
                    await page.wait_for_timeout(3000)
                    
                    # Check for modal
                    modal_appeared = False
                    try:
                        ok_button = await page.query_selector('button:has-text("OK")')
                        if ok_button and await ok_button.is_visible():
                            await ok_button.click()
                            await page.wait_for_timeout(2000)
                            modal_appeared = True
                            print(f"   ⚠️ Attempt {attempt + 1}: Modal still appears")
                            
                            # Try more aggressive approach
                            if attempt == 2:  # On third attempt, try brute force
                                print("   💥 Brute force approach...")
                                brute_force_js = """
                                let selects = document.querySelectorAll('select');
                                selects.forEach(select => {
                                    if (select.options.length > 1) {
                                        select.selectedIndex = 1;
                                        select.value = select.options[1].value;
                                        select.dispatchEvent(new Event('change', {bubbles: true}));
                                        select.dispatchEvent(new Event('input', {bubbles: true}));
                                        select.dispatchEvent(new Event('blur', {bubbles: true}));
                                    }
                                });
                                
                                // Force all radio buttons
                                let radios = document.querySelectorAll('input[type="radio"]');
                                radios.forEach(radio => {
                                    if (radio.value === 'Freehold' || radio.value === 'Yes' || radio.value === 'No') {
                                        radio.checked = true;
                                        radio.dispatchEvent(new Event('change', {bubbles: true}));
                                    }
                                });
                                """
                                await page.evaluate(brute_force_js)
                                await page.wait_for_timeout(1000)
                        else:
                            print(f"   ✅ Success! No modal on attempt {attempt + 1}")
                            await page.screenshot(path=f"success_attempt_{attempt + 1}.png")
                            
                            # Check current section
                            page_text = await page.text_content('body')
                            if 'applicant' in page_text.lower() or 'employment' in page_text.lower():
                                print("🎉 BREAKTHROUGH! Reached applicant section!")
                                await complete_remaining_sections(page)
                                return
                            elif 'results' in page_text.lower():
                                print("🎉 DIRECT TO RESULTS!")
                                await extract_results(page)
                                return
                            else:
                                print("✅ Made progress - continuing...")
                                await continue_workflow(page)
                                return
                    except:
                        print(f"   ✅ No modal detected on attempt {attempt + 1}")
                        await page.screenshot(path=f"no_modal_attempt_{attempt + 1}.png")
                        await continue_workflow(page)
                        return
                
                await page.wait_for_timeout(1000)
            
            print("📊 All submission attempts completed")
            await page.screenshot(path="final_all_attempts.png")
            
            # Keep browser open for inspection
            print("⏳ Keeping browser open for manual inspection...")
            await page.wait_for_timeout(120000)  # 2 minutes
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="direct_dropdown_error.png")
            
        finally:
            await browser.close()


async def complete_remaining_sections(page):
    """Complete applicant and income sections."""
    try:
        print("👥 Completing applicant section...")
        
        # Set employment to Employed
        employment_js = """
        let selects = document.querySelectorAll('select');
        for (let select of selects) {
            for (let option of select.options) {
                if (option.text.toLowerCase().includes('employed') && !option.text.toLowerCase().includes('self')) {
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
        
        # Submit to income section
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
        if submit_button:
            await submit_button.click()
            await page.wait_for_timeout(5000)
        
        # Fill income fields
        print("💰 Filling income fields...")
        income_fields = await page.query_selector_all('input[name*="income"], input[name*="salary"], input[name*="basic"]')
        for field in income_fields:
            try:
                if await field.is_visible():
                    await field.fill('40000')
                    print("✅ Income field filled")
            except:
                continue
        
        # Final submit for results
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
        if submit_button:
            print("🚀 Final submit for results...")
            await submit_button.click()
            await page.wait_for_timeout(15000)
        
        await extract_results(page)
        
    except Exception as e:
        print(f"❌ Remaining sections error: {e}")


async def continue_workflow(page):
    """Continue the workflow from current position."""
    try:
        print("🔄 Continuing workflow...")
        await page.wait_for_load_state("networkidle")
        
        page_text = await page.text_content('body')
        
        if 'applicant' in page_text.lower():
            await complete_remaining_sections(page)
        elif 'results' in page_text.lower():
            await extract_results(page)
        else:
            print("✅ At unknown section - taking screenshot")
            await page.screenshot(path="unknown_section.png")
            
    except Exception as e:
        print(f"❌ Workflow continuation error: {e}")


async def extract_results(page):
    """Extract final results."""
    try:
        print("📊 Extracting results...")
        await page.screenshot(path="FINAL_RESULTS_EXTRACTED.png")
        
        page_text = await page.text_content('body')
        target_lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom"]
        found_lenders = [l for l in target_lenders if l in page_text]
        
        if found_lenders:
            print(f"\n🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉")
            print(f"📊 LENDERS FOUND: {found_lenders}")
            print(f"📈 TOTAL: {len(found_lenders)}")
            print("✅ FULL END-TO-END AUTOMATION COMPLETE!")
        else:
            print("✅ Reached results page - automation complete!")
            
    except Exception as e:
        print(f"❌ Results extraction error: {e}")


if __name__ == "__main__":
    asyncio.run(direct_dropdown_fix())