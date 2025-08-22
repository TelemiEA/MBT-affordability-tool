"""
Debug clicking on credit case rows
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def debug_row_clicking():
    """Debug clicking on the credit case row."""
    
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
        
        case_reference = "C . E-Single"
        print(f"🔍 Looking for credit case: {case_reference}")
        
        # Find the row containing the case reference text
        rows = await page.query_selector_all('tr')
        print(f"📋 Found {len(rows)} table rows")
        
        # First, let's see what text is in each row
        print("\n📝 Row contents:")
        for i, row in enumerate(rows):
            try:
                row_text = await row.text_content()
                if row_text and row_text.strip():
                    cleaned_row = ' '.join(row_text.strip().split())[:100]  # Clean and limit
                    print(f"   Row {i+1}: {cleaned_row}")
                    if 'E-Single' in row_text or 'C.' in row_text:
                        print(f"      ⭐ This row might be our target!")
            except:
                continue
        
        print(f"\n🔍 Now looking for rows containing '{case_reference}' or similar...")
        
        for i, row in enumerate(rows):
            try:
                row_text = await row.text_content()
                # Try different variations
                if row_text and (case_reference in row_text or 
                                'E-Single' in row_text or
                                'C.E-Single' in row_text or
                                'C . E-Single' in row_text):
                    print(f"   ✅ Row {i+1} contains '{case_reference}'")
                    print(f"   📝 Full row text: {row_text.strip()}")
                    
                    # Look for clickable elements in this row
                    clickable_elements = await row.query_selector_all('a, button, [onclick], td')
                    print(f"   🔍 Found {len(clickable_elements)} potentially clickable elements in row")
                    
                    for j, element in enumerate(clickable_elements):
                        try:
                            element_text = await element.text_content()
                            element_tag = await element.evaluate('el => el.tagName')
                            if element_text:
                                cleaned_text = element_text.strip()[:50]  # Limit length
                                print(f"      Element {j+1} ({element_tag}): '{cleaned_text}'")
                                
                                # Try to click elements that look like reference numbers
                                if 'QX' in cleaned_text or 'RESI' in cleaned_text:
                                    print(f"      🎯 This looks clickable: '{cleaned_text}'")
                                    
                                    # Try clicking it
                                    try:
                                        await element.click()
                                        await page.wait_for_load_state("networkidle", timeout=10000)
                                        await page.wait_for_timeout(2000)
                                        
                                        # Check if we navigated away from dashboard
                                        current_url = page.url
                                        if 'dashboard/quotes' not in current_url:
                                            print(f"      ✅ Successfully clicked! New URL: {current_url}")
                                            
                                            # Take screenshot of the opened case
                                            await page.screenshot(path="opened_credit_case.png", full_page=True)
                                            print("      📷 Screenshot saved: opened_credit_case.png")
                                            
                                            print(f"\n🔍 Waiting 10 seconds for inspection...")
                                            await page.wait_for_timeout(10000)
                                            return
                                        else:
                                            print(f"      ⚠️ Click didn't navigate away, still on dashboard")
                                    except Exception as click_error:
                                        print(f"      ❌ Click failed: {click_error}")
                        except Exception as element_error:
                            print(f"      ⚠️ Error with element {j+1}: {element_error}")
                            continue
                    
                    break  # Found the row, no need to check others
            except:
                continue
        else:
            print(f"❌ Could not find row containing '{case_reference}'")
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
    
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(debug_row_clicking())