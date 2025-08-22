"""
JavaScript Form Completion - Direct DOM manipulation
Use JavaScript to directly set form values and trigger events
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def javascript_form_completion():
    """Use JavaScript to directly manipulate form elements."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            print("🎯 JAVASCRIPT FORM COMPLETION - FULL AUTOMATION")
            print("Strategy: Direct DOM manipulation with JavaScript")
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
            
            # === JAVASCRIPT FORM MANIPULATION ===
            print("\n🎯 JAVASCRIPT FORM MANIPULATION")
            print("-" * 40)
            
            # Take screenshot before
            await page.screenshot(path="js_before_completion.png")
            
            # Execute comprehensive JavaScript to complete all form elements
            completion_js = """
            (function() {
                console.log('Starting form completion...');
                let results = { completed: [], errors: [] };
                
                try {
                    // 1. Set Freehold radio button
                    const freeholdRadio = document.querySelector('input[type="radio"][value="Freehold"]');
                    if (freeholdRadio) {
                        freeholdRadio.checked = true;
                        freeholdRadio.dispatchEvent(new Event('change', {bubbles: true}));
                        results.completed.push('Freehold radio set');
                    }
                    
                    // 2. Handle all select elements with comprehensive event triggering
                    const selects = document.querySelectorAll('select');
                    selects.forEach((select, index) => {
                        if (select.options && select.options.length > 1) {
                            // Find appropriate option based on context
                            let optionToSelect = 1; // Default to first option
                            
                            // Look for specific options we want
                            for (let i = 0; i < select.options.length; i++) {
                                const optionText = select.options[i].text.toLowerCase();
                                
                                // Reason for mortgage options
                                if (optionText.includes('first-time') || optionText.includes('purchase') || optionText.includes('buy')) {
                                    optionToSelect = i;
                                    break;
                                }
                                
                                // Property type options
                                if (optionText.includes('house') || optionText.includes('terraced') || optionText.includes('detached')) {
                                    optionToSelect = i;
                                    break;
                                }
                                
                                // Term options
                                if (optionText.includes('35') || optionText.includes('year')) {
                                    optionToSelect = i;
                                    break;
                                }
                            }
                            
                            // Set the option
                            const oldValue = select.value;
                            select.selectedIndex = optionToSelect;
                            select.value = select.options[optionToSelect].value;
                            
                            // Trigger all possible events
                            const events = ['focus', 'click', 'mousedown', 'mouseup', 'input', 'change', 'blur'];
                            events.forEach(eventType => {
                                const event = new Event(eventType, { bubbles: true, cancelable: true });
                                select.dispatchEvent(event);
                            });
                            
                            // Also trigger React/Angular style events
                            if (window.React || window.ng) {
                                select.dispatchEvent(new CustomEvent('input', { bubbles: true }));
                                select.dispatchEvent(new CustomEvent('change', { bubbles: true }));
                            }
                            
                            results.completed.push(`Select ${index}: ${select.options[optionToSelect].text}`);
                        }
                    });
                    
                    // 3. Handle any hidden inputs that might control the dropdowns
                    const hiddenInputs = document.querySelectorAll('input[type="hidden"]');
                    hiddenInputs.forEach(input => {
                        const name = input.name || input.id || '';
                        if (name.toLowerCase().includes('reason')) {
                            input.value = 'Purchase';
                            input.dispatchEvent(new Event('change', {bubbles: true}));
                            results.completed.push('Hidden reason input set');
                        }
                        if (name.toLowerCase().includes('property') || name.toLowerCase().includes('type')) {
                            input.value = 'House';
                            input.dispatchEvent(new Event('change', {bubbles: true}));
                            results.completed.push('Hidden property input set');
                        }
                    });
                    
                    // 4. Set any term checkboxes
                    const termCheckboxes = document.querySelectorAll('input[type="checkbox"]');
                    termCheckboxes.forEach(checkbox => {
                        const parent = checkbox.closest('div, span, label');
                        if (parent && parent.textContent) {
                            const text = parent.textContent.toLowerCase();
                            if (text.includes('35') || text.includes('year') || text.includes('term')) {
                                checkbox.checked = true;
                                checkbox.dispatchEvent(new Event('change', {bubbles: true}));
                                results.completed.push('Term checkbox set');
                            }
                        }
                    });
                    
                    // 5. Force update any Vue.js or Angular bindings
                    if (window.Vue) {
                        // Trigger Vue updates
                        const vueComponents = document.querySelectorAll('[data-v-]');
                        vueComponents.forEach(comp => {
                            if (comp.__vue__) {
                                comp.__vue__.$forceUpdate();
                            }
                        });
                    }
                    
                    // 6. Try to find and click any dropdown buttons/triggers
                    const dropdownTriggers = document.querySelectorAll('.dropdown-toggle, .select-trigger, [role="combobox"]');
                    dropdownTriggers.forEach(trigger => {
                        trigger.click();
                        setTimeout(() => {
                            // Look for options that appear
                            const options = document.querySelectorAll('.dropdown-item, .option, .select-option');
                            if (options.length > 0) {
                                options[0].click(); // Click first option
                                results.completed.push('Dropdown trigger option selected');
                            }
                        }, 500);
                    });
                    
                } catch (error) {
                    results.errors.push(error.message);
                }
                
                return results;
            })();
            """
            
            print("🔧 Executing comprehensive JavaScript form completion...")
            js_results = await page.evaluate(completion_js)
            
            print(f"📊 JavaScript execution results:")
            print(f"   Completed: {js_results.get('completed', [])}")
            print(f"   Errors: {js_results.get('errors', [])}")
            
            await page.wait_for_timeout(3000)
            await page.screenshot(path="js_after_completion.png")
            
            # Test submission
            print("\n🚀 Testing submission after JavaScript completion...")
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                # Check result
                try:
                    modal_button = await page.query_selector('button:has-text("OK")')
                    if modal_button and await modal_button.is_visible():
                        print("⚠️ Still validation errors after JavaScript")
                        await page.screenshot(path="js_validation_errors.png")
                        await modal_button.click()
                        
                        # Final attempt with even more aggressive JavaScript
                        print("\n🔥 FINAL AGGRESSIVE JAVASCRIPT ATTEMPT...")
                        await final_aggressive_js(page)
                        
                    else:
                        print("🎉 SUCCESS! JavaScript form completion worked!")
                        await page.screenshot(path="js_success.png")
                        await continue_automation(page)
                        return
                        
                except:
                    print("🎉 SUCCESS! No modal - JavaScript worked!")
                    await continue_automation(page)
                    return
            
            # Keep browser open for inspection
            print("\n⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(120000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="js_error.png")
            
        finally:
            await browser.close()


async def final_aggressive_js(page):
    """Final aggressive JavaScript attempt."""
    try:
        final_js = """
        // Final aggressive form completion
        (function() {
            // Force set all select elements to their first non-empty option
            document.querySelectorAll('select').forEach(select => {
                if (select.options.length > 1) {
                    select.selectedIndex = 1;
                    select.value = select.options[1].value;
                    
                    // Create and dispatch multiple event types
                    ['input', 'change', 'blur', 'click'].forEach(eventType => {
                        const event = new Event(eventType, { bubbles: true, cancelable: true });
                        select.dispatchEvent(event);
                    });
                }
            });
            
            // Force click all radio buttons we want
            const freeholdRadio = document.querySelector('input[value="Freehold"]');
            if (freeholdRadio) {
                freeholdRadio.checked = true;
                freeholdRadio.click();
            }
            
            // Force set any data attributes or properties
            document.querySelectorAll('select').forEach(select => {
                if (select.options.length > 1) {
                    select.setAttribute('data-selected', select.options[1].value);
                    if (select.dataset) {
                        select.dataset.value = select.options[1].value;
                    }
                }
            });
            
            return 'Final aggressive completion executed';
        })();
        """
        
        result = await page.evaluate(final_js)
        print(f"🔥 Final aggressive result: {result}")
        
        await page.wait_for_timeout(2000)
        
        # Test submission one more time
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
        if submit_button:
            await submit_button.click()
            await page.wait_for_timeout(5000)
            
            try:
                modal_button = await page.query_selector('button:has-text("OK")')
                if modal_button and await modal_button.is_visible():
                    print("⚠️ Final attempt still has validation errors")
                    await modal_button.click()
                else:
                    print("🎉 FINAL ATTEMPT SUCCEEDED!")
                    await continue_automation(page)
            except:
                print("🎉 FINAL ATTEMPT SUCCEEDED!")
                await continue_automation(page)
                
    except Exception as e:
        print(f"❌ Final aggressive error: {e}")


async def continue_automation(page):
    """Continue automation after successful form completion."""
    try:
        print("\n🎉 FORM COMPLETION SUCCESSFUL - CONTINUING AUTOMATION!")
        print("=" * 60)
        
        # Continue through sections as before
        for section in range(10):
            await page.wait_for_load_state("networkidle")
            page_text = await page.text_content('body')
            
            if 'results' in page_text.lower():
                print("🎉 RESULTS FOUND!")
                await page.screenshot(path="JS_FINAL_RESULTS.png")
                
                lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise"]
                found = [l for l in lenders if l in page_text]
                
                if found:
                    print(f"\n🎉🎉🎉 JAVASCRIPT AUTOMATION SUCCESS! 🎉🎉🎉")
                    print(f"📊 LENDERS: {found}")
                    print("✅ FULL AUTOMATION ACHIEVED!")
                else:
                    print("✅ Reached results page!")
                return
            
            # Quick fill and continue
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
    asyncio.run(javascript_form_completion())