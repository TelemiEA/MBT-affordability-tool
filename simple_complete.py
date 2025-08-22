"""
Simplest possible approach to complete the dropdowns.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def simple_complete():
    """Use the simplest approach to complete form."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            # Quick setup to get to the form
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
            
            print("🎯 At property section...")
            await page.screenshot(path="simple_at_property.png")
            
            # Try the simplest JavaScript approach
            simple_js = """
            const selects = document.querySelectorAll('select');
            for (let i = 0; i < selects.length; i++) {
                const select = selects[i];
                if (select.options.length > 1) {
                    select.selectedIndex = 1;
                    const event = new Event('change', { bubbles: true });
                    select.dispatchEvent(event);
                }
            }
            
            // Set radio buttons
            const freehold = document.querySelector('input[value="Freehold"]');
            if (freehold) {
                freehold.checked = true;
                freehold.dispatchEvent(new Event('change'));
            }
            """
            
            await page.evaluate(simple_js)
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path="simple_after_js.png")
            
            # Submit
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(5000)
            
            # Check result
            url = page.url
            text = await page.text_content('body')
            
            await page.screenshot(path="simple_final.png")
            
            print(f"Final URL: {url}")
            
            if 'applicant' in text.lower() or 'employment' in text.lower():
                print("🎉 SUCCESS! Reached applicant section!")
            elif 'results' in text.lower():
                print("🎉 SUCCESS! Reached results!")
            elif 'please' in text.lower():
                print("❌ Still validation errors")
            else:
                print("⚠️ Unknown state")
            
            # Keep open
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="simple_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_complete())