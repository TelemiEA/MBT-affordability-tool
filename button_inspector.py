"""
Button Inspector - Find all buttons on the page to locate the green arrow
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def inspect_buttons():
    """Inspect all buttons on the page to find the green arrow."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            print("🔍 BUTTON INSPECTOR - Finding the Green Arrow")
            print("=" * 50)
            
            # Login and navigate to the search point
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
            
            # Navigate through to the search area
            # Navigate to income section
            for attempt in range(5):
                page_text = await page.text_content('body')
                
                if any(term in page_text.lower() for term in ['annual basic salary', 'net profit', 'search']):
                    print("✅ Reached search area")
                    break
                
                # Look for Next/Continue buttons
                next_buttons = await page.query_selector_all('button, input[type="submit"]')
                for button in next_buttons:
                    try:
                        text = await button.text_content() or ''
                        if any(term in text.lower() for term in ['next', 'continue', 'save']):
                            await button.click()
                            await page.wait_for_load_state("networkidle")
                            await page.wait_for_timeout(2000)
                            print(f"   ✅ Clicked: {text}")
                            break
                    except:
                        continue
            
            # Take screenshot
            await page.screenshot(path="button_inspection_page.png")
            
            # INSPECT ALL BUTTONS
            print("\\n🔍 INSPECTING ALL BUTTONS ON PAGE:")
            print("-" * 40)
            
            # Get all button-like elements
            button_selectors = [
                'button',
                'input[type="submit"]',
                'input[type="button"]',
                'a[class*="btn"]',
                '.btn',
                '[role="button"]'
            ]
            
            all_buttons = []
            for selector in button_selectors:
                buttons = await page.query_selector_all(selector)
                all_buttons.extend(buttons)
            
            print(f"Found {len(all_buttons)} potential buttons")
            
            for i, button in enumerate(all_buttons):
                try:
                    if await button.is_visible():
                        text = await button.text_content() or ''
                        html = await button.inner_html() or ''
                        classes = await button.get_attribute('class') or ''
                        style = await button.get_attribute('style') or ''
                        
                        # Check for green indicators
                        is_green = any(indicator in (classes + style + html).lower() 
                                     for indicator in ['green', 'success', 'play', 'run', 'arrow'])
                        
                        # Check for search indicators  
                        is_search = any(indicator in text.lower() 
                                      for indicator in ['search', 'run', 'get results', 'calculate'])
                        
                        if is_green or is_search or 'search' in text.lower():
                            print(f"\\n🎯 BUTTON {i+1} - POTENTIAL TARGET:")
                            print(f"   Text: '{text.strip()}'")
                            print(f"   Classes: '{classes}'")
                            print(f"   Style: '{style}'")
                            print(f"   Has green indicators: {is_green}")
                            print(f"   Has search indicators: {is_search}")
                            print(f"   HTML: {html[:100]}...")
                        else:
                            print(f"Button {i+1}: '{text.strip()[:30]}'")
                            
                except Exception as e:
                    print(f"Button {i+1}: Error - {e}")
            
            print("\\n⏳ Page will stay open for manual inspection...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="button_inspection_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_buttons())