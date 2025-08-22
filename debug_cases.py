"""
Debug script to see what cases are visible on the MBT dashboard
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def debug_dashboard_cases():
    """Debug what cases are visible on the dashboard."""
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False, slow_mo=1000)
    page = await browser.new_page()
    
    try:
        print("🔐 Logging into MBT...")
        await page.goto("https://mortgagebrokertools.co.uk/signin", timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=30000)
        
        # Login
        await page.click('input[name="email"]')
        await page.keyboard.press('Control+a')
        await page.keyboard.press('Delete')
        await page.type('input[name="email"]', os.getenv("MBT_USERNAME"))
        
        await page.click('input[name="password"]')
        await page.keyboard.press('Control+a')
        await page.keyboard.press('Delete')
        await page.type('input[name="password"]', os.getenv("MBT_PASSWORD"))
        
        await page.click('input[type="submit"]')
        await page.wait_for_load_state("networkidle", timeout=30000)
        print("✅ Login successful")
        
        # Navigate to dashboard
        await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes', timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        
        print("\n🔍 Analyzing dashboard cases...")
        
        # Get all text content
        page_text = await page.text_content('body')
        
        # Look for all case references
        import re
        
        # Find QX cases (existing)
        qx_cases = re.findall(r'QX\d+', page_text)
        if qx_cases:
            print(f"📋 QX Cases found: {set(qx_cases)}")
        
        # Find C.* cases (new credit cases)
        c_cases = re.findall(r'C\.[A-Za-z-]+', page_text)
        if c_cases:
            print(f"📋 C.* Cases found: {set(c_cases)}")
        
        # Look for any text containing 'C.E' or 'C.Self'
        ce_matches = re.findall(r'C\.E[A-Za-z-]*', page_text)
        if ce_matches:
            print(f"📋 C.E* matches: {set(ce_matches)}")
            
        cself_matches = re.findall(r'C\.Self[A-Za-z-]*', page_text)
        if cself_matches:
            print(f"📋 C.Self* matches: {set(cself_matches)}")
        
        # Get all clickable elements with text
        clickable_elements = await page.query_selector_all('a, button, [onclick], [role="button"]')
        print(f"\n🔍 Found {len(clickable_elements)} clickable elements")
        
        case_like_elements = []
        for element in clickable_elements[:50]:  # Check first 50 to avoid overwhelming
            try:
                text = await element.text_content()
                if text and ('C.' in text or 'QX' in text):
                    case_like_elements.append(text.strip())
            except:
                continue
        
        if case_like_elements:
            print(f"📋 Case-like clickable elements: {set(case_like_elements)}")
        
        # Take a screenshot for manual inspection
        await page.screenshot(path="dashboard_debug.png", full_page=True)
        print(f"📷 Screenshot saved: dashboard_debug.png")
        
        print(f"\n🔍 Waiting 10 seconds for manual inspection...")
        await page.wait_for_timeout(10000)
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
    
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(debug_dashboard_cases())