"""
Final breakthrough - Complete end-to-end automation with comprehensive dropdown handling.
This addresses the exact validation errors we can see in the screenshots.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import re

load_dotenv()

async def final_breakthrough():
    """Complete the full end-to-end workflow."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            # Quick setup
            print("🔐 Setting up...")
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
            print("📝 Basic fields...")
            basic_fields = [
                ('input[name="firstname"]', 'Test'),
                ('input[name="surname"]', 'User'),
                ('input[name="email"]', 'test@example.com'),
                ('input[name="purchase"]', '1000000'),
                ('input[name="loan_amount"]', '100000')
            ]
            
            for selector, value in basic_fields:
                await page.fill(selector, value)
            
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
            
            print("🎯 Property section - comprehensive dropdown completion...")
            
            # Comprehensive approach to complete ALL required fields
            max_attempts = 5
            for attempt in range(max_attempts):
                print(f"\\n--- ATTEMPT {attempt + 1}/{max_attempts} ---")
                
                # Take screenshot
                await page.screenshot(path=f"attempt_{attempt + 1}_start.png")
                
                # Method 1: Enhanced JavaScript completion
                comprehensive_js = f"""
                console.log('=== Comprehensive Form Completion Attempt {attempt + 1} ===');
                let results = {{
                    selectsFound: 0,
                    selectsCompleted: 0,
                    radiosSet: 0,
                    errors: []
                }};
                
                try {{
                    // Find and complete ALL select dropdowns
                    const selects = document.querySelectorAll('select');
                    results.selectsFound = selects.length;
                    console.log('Found', selects.length, 'select elements');
                    
                    selects.forEach((select, index) => {{
                        try {{
                            const name = select.name || select.id || 'unnamed';
                            const options = Array.from(select.options);
                            console.log(`Select ${{index}}: name="${{name}}", options=${{options.length}}`);
                            
                            if (options.length > 1) {{
                                // Try to select based on content
                                let optionSelected = false;
                                
                                // For reason dropdown
                                if (name.toLowerCase().includes('reason') || 
                                    select.closest('*')?.textContent?.toLowerCase().includes('reason')) {{
                                    
                                    for (let i = 1; i < options.length; i++) {{
                                        const optText = options[i].text.toLowerCase();
                                        if (optText.includes('purchase') || optText.includes('buy') || 
                                            optText.includes('home') || optText.includes('remortgage')) {{
                                            select.selectedIndex = i;
                                            select.value = options[i].value;
                                            optionSelected = true;
                                            console.log('Set reason to:', options[i].text);
                                            break;
                                        }}
                                    }}
                                }}
                                
                                // For property type dropdown
                                else if (name.toLowerCase().includes('property') || name.toLowerCase().includes('type') ||
                                        select.closest('*')?.textContent?.toLowerCase().includes('property type')) {{
                                    
                                    for (let i = 1; i < options.length; i++) {{
                                        const optText = options[i].text.toLowerCase();
                                        if (optText.includes('house') || optText.includes('detached') || 
                                            optText.includes('flat') || optText.includes('apartment')) {{
                                            select.selectedIndex = i;
                                            select.value = options[i].value;
                                            optionSelected = true;
                                            console.log('Set property type to:', options[i].text);
                                            break;
                                        }}
                                    }}
                                }}
                                
                                // For region dropdown
                                else if (name.toLowerCase().includes('region') ||
                                        select.closest('*')?.textContent?.toLowerCase().includes('region')) {{
                                    
                                    for (let i = 1; i < options.length; i++) {{
                                        const optText = options[i].text.toLowerCase();
                                        if (optText.includes('england') || optText.includes('uk') || 
                                            optText.includes('london') || optText.includes('south')) {{
                                            select.selectedIndex = i;
                                            select.value = options[i].value;
                                            optionSelected = true;
                                            console.log('Set region to:', options[i].text);
                                            break;
                                        }}
                                    }}
                                }}
                                
                                // For ownership dropdown
                                else if (name.toLowerCase().includes('ownership') || name.toLowerCase().includes('tenure') ||
                                        select.closest('*')?.textContent?.toLowerCase().includes('ownership')) {{
                                    
                                    for (let i = 1; i < options.length; i++) {{
                                        const optText = options[i].text.toLowerCase();
                                        if (optText.includes('freehold') || optText.includes('owner')) {{
                                            select.selectedIndex = i;
                                            select.value = options[i].value;
                                            optionSelected = true;
                                            console.log('Set ownership to:', options[i].text);
                                            break;
                                        }}
                                    }}
                                }}
                                
                                // If no specific match, select first non-empty option
                                if (!optionSelected && options.length > 1) {{
                                    select.selectedIndex = 1;
                                    select.value = options[1].value;
                                    optionSelected = true;
                                    console.log('Set dropdown', index, 'to first option:', options[1].text);
                                }}
                                
                                if (optionSelected) {{
                                    results.selectsCompleted++;
                                    // Trigger all possible events
                                    select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                    select.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    select.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                                }}
                            }}
                        }} catch (e) {{
                            results.errors.push(`Select ${{index}}: ${{e.message}}`);
                        }}
                    }});
                    
                    // Set radio buttons
                    const radioSelections = [
                        {{ value: 'Freehold', context: 'tenure' }},
                        {{ value: 'Yes', context: 'main residence' }},
                        {{ value: 'No', context: 'debt consolidation' }},
                        {{ value: 'No', context: 'green mortgage' }},
                        {{ value: 'No', context: 'later life' }}
                    ];
                    
                    radioSelections.forEach(selection => {{
                        try {{
                            const radio = document.querySelector(`input[type="radio"][value="${{selection.value}}"]`);
                            if (radio && !radio.checked) {{
                                radio.checked = true;
                                radio.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                results.radiosSet++;
                                console.log('Set radio:', selection.context, '=', selection.value);
                            }}
                        }} catch (e) {{
                            results.errors.push(`Radio ${{selection.context}}: ${{e.message}}`);
                        }}
                    }});
                    
                }} catch (e) {{
                    results.errors.push('Main error: ' + e.message);
                }}
                
                console.log('Results:', results);
                return results;
                """
                
                js_result = await page.evaluate(comprehensive_js)
                print(f"JavaScript result: {js_result}")
                
                # Wait for form updates
                await page.wait_for_timeout(3000)
                
                # Take screenshot after JS
                await page.screenshot(path=f"attempt_{attempt + 1}_after_js.png")
                
                # Try submitting
                submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
                if submit_button:
                    await submit_button.click()
                    await page.wait_for_timeout(5000)
                    
                    # Handle modal
                    modal_appeared = False
                    try:
                        ok_button = await page.query_selector('button:has-text("OK")')
                        if ok_button and await ok_button.is_visible():
                            await ok_button.click()
                            await page.wait_for_timeout(2000)
                            modal_appeared = True
                            print("⚠️ Modal appeared - continuing attempts")
                        else:
                            print("✅ No modal - likely progressed!")
                    except:
                        pass
                    
                    await page.wait_for_load_state("networkidle")
                    
                    # Check if we progressed
                    current_url = page.url
                    page_text = await page.text_content('body')
                    
                    # Take screenshot after submit
                    await page.screenshot(path=f"attempt_{attempt + 1}_after_submit.png")
                    
                    print(f"Current URL: {current_url}")
                    
                    # Check for success
                    if not modal_appeared and ('applicant' in page_text.lower() or 
                                            'employment' in page_text.lower() or 
                                            'income' in page_text.lower()):
                        print("🎉 SUCCESS! Reached applicant/income section!")
                        
                        # Look for income fields
                        income_fields = await page.query_selector_all('input[name*="income"], input[name*="salary"], input[name*="net_profit"]')
                        visible_income = 0
                        for field in income_fields:
                            try:
                                if await field.is_visible():
                                    visible_income += 1
                            except:
                                pass
                        
                        print(f"Found {visible_income} visible income fields")
                        
                        if visible_income > 0:
                            print("🎉 BREAKTHROUGH! Ready to fill income fields!")
                            
                            # Fill income fields quickly
                            for field in income_fields[:visible_income]:
                                try:
                                    if await field.is_visible():
                                        await field.fill('40000')
                                        print("✅ Filled income field")
                                except:
                                    pass
                            
                            await page.wait_for_timeout(2000)
                            
                            # Final submit
                            final_submit = await page.query_selector('button[type="submit"], input[type="submit"]')
                            if final_submit:
                                await final_submit.click()
                                await page.wait_for_timeout(10000)
                                await page.wait_for_load_state("networkidle", timeout=30000)
                                
                                # Take final screenshot
                                await page.screenshot(path="final_results_breakthrough.png")
                                
                                # Check for results
                                final_text = await page.text_content('body')
                                
                                target_lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise"]
                                found_lenders = []
                                
                                for lender in target_lenders:
                                    if lender in final_text:
                                        # Try to extract amount
                                        pattern = rf'{re.escape(lender)}.*?£([\\d,]+)'
                                        matches = re.findall(pattern, final_text, re.IGNORECASE | re.DOTALL)
                                        if matches:
                                            amounts = [float(m.replace(',', '')) for m in matches if m.replace(',', '').isdigit()]
                                            if amounts:
                                                max_amount = max(amounts)
                                                found_lenders.append(f"{lender}: £{max_amount:,.0f}")
                                        else:
                                            found_lenders.append(f"{lender}: Found (no amount)")
                                
                                if found_lenders:
                                    print("\\n🎉 FINAL SUCCESS! LENDER RESULTS:")
                                    for result in found_lenders:
                                        print(f"   {result}")
                                    
                                    print(f"\\n📊 TOTAL: {len(found_lenders)} lenders found")
                                    return True
                                else:
                                    print("⚠️ Reached results but no target lenders found")
                        
                        return True
                    
                    elif 'please' not in page_text.lower():
                        print("✅ Progressed but checking further...")
                        # Continue to next attempt or section
                    else:
                        print(f"❌ Still have validation errors on attempt {attempt + 1}")
                        if attempt == max_attempts - 1:
                            print("⚠️ All attempts exhausted")
                else:
                    print("❌ No submit button found")
                    break
                
                # Brief pause before next attempt
                await page.wait_for_timeout(2000)
            
            print("\\n📊 Final state reached")
            await page.screenshot(path="final_state.png")
            
            # Keep browser open for inspection
            print("⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="breakthrough_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(final_breakthrough())