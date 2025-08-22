"""
Simple dropdown test - Just get to the form and manually test the dropdowns.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def simple_dropdown_test():
    """Get to the form and test dropdowns manually."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
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
            
            print("🎯 At property section - ready for manual testing")
            print("Please manually complete the dropdowns:")
            print("1. Reason for Mortgage: Select 'First-time buyer'")
            print("2. Property Type: Select any house type")
            print("3. Tenure: Click 'Freehold'")
            print("4. Region: Select any region")
            print("5. Ownership: Select any ownership type")
            print("Then click Submit and see what happens")
            
            await page.screenshot(path="manual_test_starting_point.png")
            
            # Get basic element info
            selects = await page.query_selector_all('select')
            print(f"\nFound {len(selects)} select elements")
            
            for i, select in enumerate(selects):
                try:
                    name = await select.get_attribute('name')
                    options = await select.query_selector_all('option')
                    option_texts = []
                    for opt in options:
                        text = await opt.text_content()
                        option_texts.append(text)
                    
                    print(f"Select {i}: name='{name}', options={option_texts}")
                    
                except Exception as e:
                    print(f"Select {i}: Error getting info - {e}")
            
            # Try a simple select operation
            print("\n🔧 Trying simple select operations...")
            
            if len(selects) >= 2:
                try:
                    # Try first select (reason)
                    print("Trying first select (reason)...")
                    first_select = selects[0]
                    await first_select.select_option(index=1)
                    print("✅ First select completed")
                    
                    await page.wait_for_timeout(2000)
                    
                    # Try second select (property type)
                    print("Trying second select (property type)...")
                    second_select = selects[1]
                    await second_select.select_option(index=1)
                    print("✅ Second select completed")
                    
                    await page.wait_for_timeout(2000)
                    
                    # Try Freehold radio
                    print("Trying Freehold radio...")
                    freehold = await page.query_selector('input[value="Freehold"]')
                    if freehold:
                        await freehold.click()
                        print("✅ Freehold clicked")
                    else:
                        print("❌ Freehold not found")
                    
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path="after_simple_operations.png")
                    
                    # Try submitting
                    print("Trying submission...")
                    submit_btn = await page.query_selector('button[type="submit"]')
                    if submit_btn:
                        await submit_btn.click()
                        await page.wait_for_timeout(5000)
                        
                        # Check for modal
                        try:
                            ok_btn = await page.query_selector('button:has-text("OK")')
                            if ok_btn and await ok_btn.is_visible():
                                print("⚠️ Modal appeared - still validation errors")
                                await ok_btn.click()
                                await page.wait_for_timeout(2000)
                            else:
                                print("✅ No modal - submission may have worked!")
                        except:
                            print("✅ No modal detected")
                        
                        await page.screenshot(path="after_simple_submission.png")
                    
                except Exception as e:
                    print(f"❌ Simple operations error: {e}")
            
            # Keep open for manual interaction
            print("\n⏳ Browser staying open for 5 minutes for manual testing...")
            print("Try manually completing the form and see what works!")
            await page.wait_for_timeout(300000)  # 5 minutes
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="simple_test_error.png")
            
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(simple_dropdown_test())