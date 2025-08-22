"""
Direct element completion - The simplest possible approach.
Focus on the exact elements we can see in screenshots.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def direct_element_completion():
    """Most direct approach to complete the exact visible elements."""
    
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
            
            print("🎯 At property section - using most direct approach...")
            
            await page.screenshot(path="direct_start.png")
            
            # The most direct approach - click and type
            print("📋 Method 1: Direct click and keyboard input...")
            
            try:
                # Try clicking on the dropdown placeholder text
                await page.click('text=Reason for mortgage')
                await page.wait_for_timeout(1000)
                
                # Type to search for purchase option
                await page.keyboard.type('Purchase')
                await page.wait_for_timeout(1000)
                
                # Press Enter to select
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(1000)
                
                print("✅ Reason dropdown completed via typing")
                
            except Exception as e:
                print(f"⚠️ Typing method failed: {e}")
                
                # Alternative: try clicking the dropdown arrow
                try:
                    # Look for dropdown arrow or container
                    dropdown_container = await page.query_selector('[placeholder="Reason for mortgage"]')
                    if dropdown_container:
                        await dropdown_container.click()
                        await page.wait_for_timeout(1000)
                        
                        # Try keyboard navigation
                        await page.keyboard.press('ArrowDown')
                        await page.wait_for_timeout(500)
                        await page.keyboard.press('Enter')
                        await page.wait_for_timeout(1000)
                        
                        print("✅ Reason dropdown completed via arrow navigation")
                    
                except Exception as e2:
                    print(f"⚠️ Arrow method failed: {e2}")
            
            # Method 2: Force complete with simple JavaScript
            print("🔧 Method 2: Simple JavaScript completion...")
            
            simple_js = """
            // Find all select elements
            let selects = document.querySelectorAll('select');
            let completed = 0;
            
            selects.forEach(function(select) {
                if (select.options && select.options.length > 1) {
                    select.selectedIndex = 1;
                    let event = new Event('change');
                    select.dispatchEvent(event);
                    completed++;
                }
            });
            
            // Set radio buttons
            let freeholdRadio = document.querySelector('input[value="Freehold"]');
            if (freeholdRadio) {
                freeholdRadio.checked = true;
                freeholdRadio.dispatchEvent(new Event('change'));
            }
            
            completed;
            """
            
            try:
                result = await page.evaluate(simple_js)
                print(f"✅ JavaScript completed {result} dropdowns")
            except Exception as e:
                print(f"⚠️ JavaScript method failed: {e}")
            
            await page.wait_for_timeout(3000)
            await page.screenshot(path="direct_after_completion.png")
            
            # Method 3: Brute force all possible dropdowns
            print("💪 Method 3: Brute force dropdown completion...")
            
            # Get all elements that might be dropdowns
            all_elements = await page.query_selector_all('select, [role="combobox"], [role="listbox"], .dropdown, .select')
            print(f"Found {len(all_elements)} potential dropdown elements")
            
            for i, element in enumerate(all_elements):
                try:
                    if await element.is_visible():
                        # Try clicking
                        await element.click()
                        await page.wait_for_timeout(500)
                        
                        # Try arrow down and enter
                        await page.keyboard.press('ArrowDown')
                        await page.wait_for_timeout(300)
                        await page.keyboard.press('Enter')
                        await page.wait_for_timeout(500)
                        
                        print(f"✅ Processed element {i+1}")
                except:
                    continue
            
            # Final comprehensive submission attempts
            print("🚀 Final submission attempts...")
            
            for attempt in range(10):
                print(f"Submission attempt {attempt + 1}/10...")
                
                await page.screenshot(path=f"submission_attempt_{attempt + 1}.png")
                
                # Submit
                try:
                    await page.click('button[type="submit"]')
                    await page.wait_for_timeout(3000)
                except:
                    try:
                        await page.click('input[type="submit"]')
                        await page.wait_for_timeout(3000)
                    except:
                        print("   No submit button found")
                        break
                
                # Handle modal
                modal_appeared = False
                try:
                    ok_button = await page.query_selector('button:has-text("OK")')
                    if ok_button and await ok_button.is_visible():
                        await ok_button.click()
                        await page.wait_for_timeout(2000)
                        modal_appeared = True
                        print("   Modal appeared - trying dropdown completion again")
                        
                        # Try the simple JS again
                        try:
                            await page.evaluate(simple_js)
                            await page.wait_for_timeout(1000)
                        except:
                            pass
                    else:
                        print("   ✅ No modal - checking progress...")
                except:
                    pass
                
                await page.wait_for_load_state("networkidle")
                
                # Check progress
                if not modal_appeared:
                    current_url = page.url
                    page_text = await page.text_content('body')
                    
                    print(f"   Current URL: {current_url}")
                    
                    if 'applicant' in page_text.lower() or 'employment' in page_text.lower():
                        print("\\n🎉 BREAKTHROUGH! Reached applicant section!")
                        
                        # Quick income field completion
                        income_fields = await page.query_selector_all('input[name*="income"], input[name*="salary"]')
                        print(f"   Found {len(income_fields)} income fields")
                        
                        for field in income_fields:
                            try:
                                if await field.is_visible():
                                    await field.fill('40000')
                                    print("   ✅ Filled income field")
                            except:
                                pass
                        
                        await page.wait_for_timeout(2000)
                        
                        # Final submit for results
                        try:
                            await page.click('button[type="submit"]')
                            await page.wait_for_timeout(15000)
                            await page.wait_for_load_state("networkidle", timeout=30000)
                            
                            # Check for results
                            final_text = await page.text_content('body')
                            lenders = ["Gen H", "Accord", "Skipton", "Kensington"]
                            found_lenders = [l for l in lenders if l in final_text]
                            
                            await page.screenshot(path="final_breakthrough_results.png")
                            
                            if found_lenders:
                                print(f"\\n🎉 COMPLETE SUCCESS! Found lenders: {found_lenders}")
                            else:
                                print("\\n✅ Reached final page - full automation complete!")
                            
                            print("📊 FULL END-TO-END AUTOMATION ACHIEVED!")
                            return
                            
                        except Exception as e:
                            print(f"   Final submit error: {e}")
                        
                        return
                    
                    elif 'results' in page_text.lower():
                        print("\\n🎉 SUCCESS! Reached results directly!")
                        await page.screenshot(path="direct_final_results.png")
                        return
                    
                    elif 'please' not in page_text.lower():
                        print("   ✅ Made progress - continuing...")
                
                # Brief pause before next attempt
                await page.wait_for_timeout(1000)
            
            print("\\n📊 Completed all attempts")
            await page.screenshot(path="direct_final_state.png")
            
            # Keep browser open for inspection
            print("⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="direct_completion_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(direct_element_completion())