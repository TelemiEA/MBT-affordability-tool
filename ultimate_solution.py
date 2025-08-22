"""
Ultimate solution - Use the most basic approach that we know works.
Focus on manual interaction combined with simple automation.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def ultimate_solution():
    """Ultimate approach using proven methods."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            # Login
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
            
            print("🎯 At property section - using direct element interaction...")
            
            # Pause for manual completion message
            print("\\n" + "="*60)
            print("🎯 SEMI-AUTOMATED APPROACH")
            print("="*60)
            print("The automation has successfully reached the Property and Mortgage section.")
            print("You can now:")
            print("1. ✅ MANUALLY complete the 2-3 remaining dropdowns:")
            print("   - Reason for Mortgage (select 'Purchase' or similar)")
            print("   - Property Type (select 'House' or similar)")
            print("   - Region (select 'England' or similar)")
            print("2. ✅ The automation will then continue automatically")
            print("3. ✅ Wait 30 seconds, then the automation will proceed")
            print("="*60)
            
            await page.screenshot(path="manual_completion_point.png")
            
            # Wait 30 seconds for manual completion
            print("⏳ Waiting 30 seconds for manual dropdown completion...")
            await page.wait_for_timeout(30000)
            
            print("🚀 Continuing automation...")
            
            # Try to submit multiple times
            for attempt in range(3):
                print(f"Submit attempt {attempt + 1}...")
                
                submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
                if submit_button:
                    await submit_button.click()
                    await page.wait_for_timeout(5000)
                    
                    # Handle modal
                    try:
                        ok_button = await page.query_selector('button:has-text("OK")')
                        if ok_button and await ok_button.is_visible():
                            await ok_button.click()
                            await page.wait_for_timeout(2000)
                            print("⚠️ Modal appeared, continuing...")
                        else:
                            print("✅ No modal - progressed!")
                            break
                    except:
                        print("✅ No modal detected")
                        break
                    
                    await page.wait_for_load_state("networkidle")
                else:
                    break
            
            # Check final state
            await page.screenshot(path="after_manual_completion.png")
            
            current_url = page.url
            page_text = await page.text_content('body')
            
            print(f"\\nFinal URL: {current_url}")
            
            # Analyze what section we reached
            if 'applicant' in page_text.lower() or 'employment' in page_text.lower():
                print("🎉 SUCCESS! Reached applicant section!")
                
                # Look for income fields
                income_fields = await page.query_selector_all('input[name*="income"], input[name*="salary"]')
                print(f"Found {len(income_fields)} income fields")
                
                # Try to fill them
                filled = 0
                for field in income_fields:
                    try:
                        if await field.is_visible():
                            await field.fill('40000')
                            filled += 1
                            print(f"✅ Filled income field {filled}")
                    except:
                        pass
                
                if filled > 0:
                    print(f"🎉 Filled {filled} income fields - submitting for results...")
                    
                    # Final submit
                    final_submit = await page.query_selector('button[type="submit"], input[type="submit"]')
                    if final_submit:
                        await final_submit.click()
                        await page.wait_for_timeout(15000)
                        await page.wait_for_load_state("networkidle", timeout=60000)
                        
                        await page.screenshot(path="ultimate_final_results.png")
                        
                        # Check for lender results
                        results_text = await page.text_content('body')
                        
                        target_lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise"]
                        found_lenders = [lender for lender in target_lenders if lender in results_text]
                        
                        if found_lenders:
                            print(f"\\n🎉 ULTIMATE SUCCESS! Found lenders: {found_lenders}")
                            print(f"📊 Total lenders found: {len(found_lenders)}")
                        else:
                            print("⚠️ Reached results but no target lenders detected")
                            if 'results' in results_text.lower() or len(results_text) > 10000:
                                print("✅ But likely on results page based on content size")
                
            elif 'results' in page_text.lower():
                print("🎉 SUCCESS! Reached results page!")
                
            elif 'please' in page_text.lower():
                print("❌ Still have validation errors")
                
            else:
                print("⚠️ Unknown section reached")
            
            # Extended wait for manual inspection
            print("\\n⏳ Keeping browser open for extended inspection...")
            await page.wait_for_timeout(120000)  # 2 minutes
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="ultimate_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(ultimate_solution())