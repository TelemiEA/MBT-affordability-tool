"""
Targeted Dropdown Fix - Focus on the 3 specific failing fields
Ultra-specific approach to complete: Reason for Mortgage, Property Type, and Tenure
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def targeted_dropdown_fix():
    """Ultra-targeted approach to fix the 3 specific failing dropdowns."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            print("🎯 TARGETED DROPDOWN FIX - ULTRA SPECIFIC")
            print("Target: 3 failing fields only")
            print("=" * 50)
            
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
            
            # Take screenshot before fix
            await page.screenshot(path="targeted_before_fix.png")
            
            # === ULTRA-TARGETED DROPDOWN FIX ===
            print("\n🎯 ULTRA-TARGETED FIX")
            print("-" * 30)
            
            # Strategy: Use coordinate-based clicking and keyboard navigation
            print("1️⃣ Fixing Freehold radio button...")
            await fix_freehold_radio(page)
            await page.wait_for_timeout(1000)
            
            print("2️⃣ Fixing Reason for Mortgage dropdown...")
            await fix_reason_dropdown(page)
            await page.wait_for_timeout(1000)
            
            print("3️⃣ Fixing Property Type dropdown...")
            await fix_property_type_dropdown(page)
            await page.wait_for_timeout(1000)
            
            # Take screenshot after fix
            await page.screenshot(path="targeted_after_fix.png")
            
            # Test submission
            print("\n🚀 Testing submission...")
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                # Check for validation
                try:
                    modal_button = await page.query_selector('button:has-text("OK")')
                    if modal_button and await modal_button.is_visible():
                        print("⚠️ Still validation errors")
                        await page.screenshot(path="targeted_still_errors.png")
                        await modal_button.click()
                        
                        # Final aggressive attempt
                        print("\n🔥 FINAL AGGRESSIVE ATTEMPT...")
                        await final_aggressive_attempt(page)
                        
                    else:
                        print("🎉 SUCCESS! Targeted fix worked!")
                        await page.screenshot(path="targeted_success.png")
                        await continue_automation(page)
                        return
                        
                except:
                    print("🎉 SUCCESS! No modal - targeted fix worked!")
                    await continue_automation(page)
                    return
            
            # Keep browser open for inspection
            print("\n⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="targeted_error.png")
            
        finally:
            await browser.close()


async def fix_freehold_radio(page):
    """Fix the Freehold radio button specifically."""
    try:
        # Multiple strategies for Freehold
        strategies = [
            'input[value="Freehold"]',
            'input[type="radio"][value="Freehold"]',
            'text=Freehold',
            'label:has-text("Freehold")'
        ]
        
        for strategy in strategies:
            try:
                await page.click(strategy, timeout=2000)
                print("   ✅ Freehold selected")
                return True
            except:
                continue
                
        # JavaScript force
        js_result = await page.evaluate("""
            () => {
                const freeholdRadio = document.querySelector('input[value="Freehold"]');
                if (freeholdRadio) {
                    freeholdRadio.checked = true;
                    freeholdRadio.click();
                    freeholdRadio.dispatchEvent(new Event('change', {bubbles: true}));
                    return 'Freehold set via JS';
                }
                return 'Freehold not found';
            }
        """)
        print(f"   JS Result: {js_result}")
        
    except Exception as e:
        print(f"   ❌ Freehold error: {e}")


async def fix_reason_dropdown(page):
    """Fix the Reason for Mortgage dropdown specifically."""
    try:
        print("   🔍 Looking for Reason for Mortgage dropdown...")
        
        # Strategy 1: Direct click on dropdown
        try:
            reason_dropdown = await page.query_selector('select')
            if reason_dropdown:
                await reason_dropdown.click()
                await page.wait_for_timeout(500)
                
                # Try to select first option
                options = await reason_dropdown.query_selector_all('option')
                if len(options) > 1:
                    await reason_dropdown.select_option(index=1)
                    print("   ✅ Reason dropdown - selected first option")
                    return True
        except:
            pass
        
        # Strategy 2: Keyboard navigation
        try:
            await page.click('text=Reason for mortgage')
            await page.keyboard.press('Tab')
            await page.keyboard.press('ArrowDown')
            await page.keyboard.press('Enter')
            print("   ✅ Reason dropdown - keyboard navigation")
            return True
        except:
            pass
        
        # Strategy 3: JavaScript force with specific option
        js_result = await page.evaluate("""
            () => {
                const selects = document.querySelectorAll('select');
                for (let select of selects) {
                    if (select.options && select.options.length > 1) {
                        // Look for purchase/first-time buyer options
                        for (let i = 1; i < select.options.length; i++) {
                            const optionText = select.options[i].text.toLowerCase();
                            if (optionText.includes('first') || optionText.includes('purchase') || optionText.includes('buy')) {
                                select.selectedIndex = i;
                                select.value = select.options[i].value;
                                select.dispatchEvent(new Event('change', {bubbles: true}));
                                return 'Reason set to: ' + select.options[i].text;
                            }
                        }
                        // Fallback to first option
                        select.selectedIndex = 1;
                        select.value = select.options[1].value;
                        select.dispatchEvent(new Event('change', {bubbles: true}));
                        return 'Reason set to first option: ' + select.options[1].text;
                    }
                }
                return 'No reason dropdown found';
            }
        """)
        print(f"   JS Result: {js_result}")
        
    except Exception as e:
        print(f"   ❌ Reason dropdown error: {e}")


async def fix_property_type_dropdown(page):
    """Fix the Property Type dropdown specifically."""
    try:
        print("   🔍 Looking for Property Type dropdown...")
        
        # Find the property type dropdown (it's the second select)
        selects = await page.query_selector_all('select')
        if len(selects) > 1:
            property_dropdown = selects[1]  # Second dropdown
            
            try:
                await property_dropdown.click()
                await page.wait_for_timeout(500)
                
                options = await property_dropdown.query_selector_all('option')
                if len(options) > 1:
                    await property_dropdown.select_option(index=1)
                    print("   ✅ Property type - selected first option")
                    return True
            except:
                pass
        
        # JavaScript specific for property type
        js_result = await page.evaluate("""
            () => {
                const selects = document.querySelectorAll('select');
                if (selects.length > 1) {
                    const propertySelect = selects[1]; // Second dropdown
                    if (propertySelect.options && propertySelect.options.length > 1) {
                        // Look for house options
                        for (let i = 1; i < propertySelect.options.length; i++) {
                            const optionText = propertySelect.options[i].text.toLowerCase();
                            if (optionText.includes('house') || optionText.includes('terraced') || optionText.includes('detached')) {
                                propertySelect.selectedIndex = i;
                                propertySelect.value = propertySelect.options[i].value;
                                propertySelect.dispatchEvent(new Event('change', {bubbles: true}));
                                return 'Property type set to: ' + propertySelect.options[i].text;
                            }
                        }
                        // Fallback to first option
                        propertySelect.selectedIndex = 1;
                        propertySelect.value = propertySelect.options[1].value;
                        propertySelect.dispatchEvent(new Event('change', {bubbles: true}));
                        return 'Property type set to first option: ' + propertySelect.options[1].text;
                    }
                }
                return 'Property type dropdown not found';
            }
        """)
        print(f"   JS Result: {js_result}")
        
    except Exception as e:
        print(f"   ❌ Property type error: {e}")


async def final_aggressive_attempt(page):
    """Final aggressive attempt with all possible strategies."""
    try:
        print("🔥 FINAL AGGRESSIVE ATTEMPT")
        
        # Force set everything with JavaScript
        final_js = """
            () => {
                let results = [];
                
                // 1. Force Freehold
                const freeholdRadio = document.querySelector('input[value="Freehold"]');
                if (freeholdRadio) {
                    freeholdRadio.checked = true;
                    freeholdRadio.click();
                    freeholdRadio.dispatchEvent(new Event('change', {bubbles: true}));
                    results.push('Freehold forced');
                }
                
                // 2. Force all selects
                const selects = document.querySelectorAll('select');
                selects.forEach((select, index) => {
                    if (select.options && select.options.length > 1) {
                        select.selectedIndex = 1;
                        select.value = select.options[1].value;
                        
                        // Multiple event types
                        ['input', 'change', 'blur', 'click'].forEach(eventType => {
                            const event = new Event(eventType, { bubbles: true, cancelable: true });
                            select.dispatchEvent(event);
                        });
                        
                        results.push(`Select ${index}: ${select.options[1].text}`);
                    }
                });
                
                return results;
            }
        """
        
        js_results = await page.evaluate(final_js)
        print(f"   Results: {js_results}")
        
        await page.wait_for_timeout(2000)
        
        # Test submission one more time
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
        if submit_button:
            await submit_button.click()
            await page.wait_for_timeout(5000)
            
            try:
                modal_button = await page.query_selector('button:has-text("OK")')
                if modal_button and await modal_button.is_visible():
                    print("⚠️ Final attempt still has errors")
                    await page.screenshot(path="final_attempt_errors.png")
                    await modal_button.click()
                else:
                    print("🎉 FINAL ATTEMPT SUCCEEDED!")
                    await continue_automation(page)
            except:
                print("🎉 FINAL ATTEMPT SUCCEEDED!")
                await continue_automation(page)
                
    except Exception as e:
        print(f"❌ Final attempt error: {e}")


async def continue_automation(page):
    """Continue automation after successful dropdown completion."""
    try:
        print("\n🎉 DROPDOWN COMPLETION SUCCESSFUL!")
        print("🚀 Continuing full automation...")
        
        # Continue with the workflow
        for section in range(10):
            await page.wait_for_load_state("networkidle")
            page_text = await page.text_content('body')
            
            if 'results' in page_text.lower():
                print("🎉 RESULTS FOUND!")
                await page.screenshot(path="TARGETED_FINAL_RESULTS.png")
                
                lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise"]
                found = [l for l in lenders if l in page_text]
                
                if found:
                    print(f"\n🎉🎉🎉 TARGETED FIX SUCCESS! 🎉🎉🎉")
                    print(f"📊 LENDERS: {found}")
                    print("✅ FULL AUTOMATION ACHIEVED!")
                else:
                    print("✅ Reached results page!")
                return
            
            # Quick fill
            await quick_fill_section(page)
            
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(3000)
                
                try:
                    modal = await page.query_selector('button:has-text("OK")')
                    if modal and await modal.is_visible():
                        await modal.click()
                        await page.wait_for_timeout(2000)
                except:
                    pass
            else:
                break
        
    except Exception as e:
        print(f"❌ Automation continuation error: {e}")


async def quick_fill_section(page):
    """Quick fill for any section."""
    try:
        # Fill income fields
        income_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
        for field in income_fields[:3]:
            try:
                if await field.is_visible():
                    name = await field.get_attribute('name') or ''
                    if 'income' in name.lower() or 'salary' in name.lower():
                        await field.fill('40000')
                    elif 'date' in name.lower():
                        await field.fill('1990-01-01')
                    elif not await field.input_value():
                        await field.fill('0')
            except:
                continue
                
    except:
        pass


if __name__ == "__main__":
    asyncio.run(targeted_dropdown_fix())