"""
Debug script to examine the actual MBT dashboard structure
and understand why case clicking is failing.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def debug_dashboard():
    """Debug the MBT dashboard to see what cases are actually available."""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Not headless so we can see
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Login first
            print("🔐 Logging into MBT...")
            await page.goto('https://mortgagebrokertools.co.uk/signin', timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            # Fill login form
            username = os.getenv('MBT_USERNAME')
            password = os.getenv('MBT_PASSWORD')
            
            if not username or not password:
                raise Exception("MBT_USERNAME and MBT_PASSWORD must be set in .env file")
            
            # Clear and fill email
            await page.click('input[name="email"]')
            await page.keyboard.press('Control+a')
            await page.keyboard.press('Delete')
            await page.type('input[name="email"]', username)
            
            # Clear and fill password
            await page.click('input[name="password"]')
            await page.keyboard.press('Control+a')
            await page.keyboard.press('Delete')
            await page.type('input[name="password"]', password)
            
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle", timeout=30000)
            print("✅ Login successful")
            
            # Navigate to dashboard 
            print("\n📋 Navigating to dashboard...")
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
            # Get all table rows
            print("\n🔍 Examining dashboard rows...")
            rows = await page.query_selector_all('tr')
            
            credit_cases = []
            all_cases = []
            
            for i, row in enumerate(rows):
                try:
                    row_text = await row.text_content()
                    if row_text and 'QX' in row_text:
                        all_cases.append(row_text.strip())
                        if 'C .' in row_text:
                            credit_cases.append(row_text.strip())
                            print(f"   Credit case found: {row_text.strip()}")
                except:
                    continue
            
            print(f"\n📊 Summary:")
            print(f"   Total cases with QX: {len(all_cases)}")
            print(f"   Credit cases found: {len(credit_cases)}")
            
            if credit_cases:
                print(f"\n💳 Credit cases details:")
                for case in credit_cases:
                    print(f"   {case}")
                    
                # Test clicking on the first credit case
                print(f"\n🧪 Testing click on first credit case...")
                target_case = credit_cases[0]
                
                # Try to find and click the case
                rows = await page.query_selector_all('tr')
                clicked = False
                
                for row in rows:
                    try:
                        row_text = await row.text_content()
                        if row_text and target_case.split()[0] in row_text:  # Match QX number
                            print(f"   Found matching row: {row_text[:100]}...")
                            
                            # Look for clickable links in this row
                            links = await row.query_selector_all('a')
                            for link in links:
                                link_text = await link.text_content()
                                if link_text and 'QX' in link_text:
                                    print(f"   Found clickable QX link: {link_text}")
                                    await link.click()
                                    clicked = True
                                    break
                            
                            if clicked:
                                break
                    except:
                        continue
                
                if clicked:
                    await page.wait_for_load_state("networkidle")
                    await page.wait_for_timeout(2000)
                    print("   ✅ Successfully clicked case!")
                    print(f"   Current URL: {page.url}")
                else:
                    print("   ❌ Could not click any case")
            else:
                print("\n❌ No credit cases found!")
                print("\n📋 All cases found:")
                for case in all_cases[:10]:  # Show first 10
                    print(f"   {case}")
            
            # Keep browser open for manual inspection
            print(f"\n⏸️  Browser staying open for inspection...")
            print(f"   Press Enter to close...")
            input()
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_dashboard())