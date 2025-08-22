"""
Test Criteria Search - Specifically test clicking RESIDENTIAL button
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def test_criteria_search():
    """Test clicking the RESIDENTIAL search button."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            print("🔍 TESTING CRITERIA SEARCH")
            print("=" * 50)
            
            # Login and navigate to criteria search
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            print("✅ Login successful")
            
            # Navigate to a case
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
            # Open E.Single case
            await page.click('text=QX002187461')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            print("✅ Case opened")
            
            # Navigate through sections to get to criteria search
            # Keep clicking next/continue until we reach criteria search
            for attempt in range(10):
                page_text = await page.text_content('body')
                current_url = page.url
                
                print(f"Attempt {attempt + 1}: {current_url}")
                
                if 'Criteria Search' in page_text:
                    print("✅ Reached Criteria Search page!")
                    break
                
                # Look for Next/Continue/Play buttons
                next_buttons = await page.query_selector_all('button, input[type="submit"]')
                clicked_something = False
                
                for button in next_buttons:
                    try:
                        if not await button.is_visible():
                            continue
                            
                        text = await button.text_content() or ''
                        html = await button.inner_html() or ''
                        
                        # Look for next/continue buttons OR play buttons
                        if any(term in text.lower() for term in ['next', 'continue', 'save']) or 'zmdi-play' in html:
                            await button.click()
                            await page.wait_for_load_state("networkidle")
                            await page.wait_for_timeout(3000)
                            print(f"   ✅ Clicked: {text.strip()}")
                            clicked_something = True
                            break
                    except Exception as e:
                        continue
                
                if not clicked_something:
                    print("   ⚠️ No clickable buttons found")
                    break
            
            # Take screenshot
            await page.screenshot(path="criteria_search_test.png")
            
            # Now test clicking RESIDENTIAL button
            page_text = await page.text_content('body')
            if 'Criteria Search' in page_text:
                print("\n🎯 TESTING RESIDENTIAL BUTTON CLICK")
                print("-" * 40)
                
                # Look for RESIDENTIAL button
                residential_selectors = [
                    'button:has-text("RESIDENTIAL")',
                    'input[value="RESIDENTIAL"]',
                    ':text("RESIDENTIAL")',
                    '[value="RESIDENTIAL"]'
                ]
                
                button_found = False
                for selector in residential_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element and await element.is_visible():
                            print(f"✅ Found RESIDENTIAL button: {selector}")
                            await element.click()
                            print("⏳ Clicked RESIDENTIAL, waiting for results...")
                            
                            await page.wait_for_load_state("networkidle", timeout=60000)
                            await page.wait_for_timeout(10000)
                            
                            # Check results
                            new_url = page.url
                            new_text = await page.text_content('body')
                            
                            print(f"📍 New URL: {new_url}")
                            print(f"📄 Has lender offers: {'offer' in new_text.lower()}")
                            print(f"📄 Has amounts: {'£' in new_text}")
                            
                            await page.screenshot(path="after_residential_click.png")
                            button_found = True
                            break
                    except Exception as e:
                        print(f"Failed {selector}: {e}")
                        continue
                
                if not button_found:
                    print("❌ RESIDENTIAL button not found")
            else:
                print("❌ Not on Criteria Search page")
            
            print("\n⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="criteria_search_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_criteria_search())