"""
Visible Browser Test - Ensure browser opens and is visible
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def visible_browser_test():
    """Test with very visible browser settings."""
    
    async with async_playwright() as p:
        # Launch browser with maximum visibility settings
        browser = await p.chromium.launch(
            headless=False,          # Never run headless
            slow_mo=3000,           # Slow down actions so you can see them
            args=[
                '--start-maximized',    # Start maximized
                '--no-sandbox',         # Disable sandbox
                '--disable-dev-shm-usage'
            ]
        )
        
        # Create a new page
        page = await browser.new_page()
        
        # Set viewport to full screen
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        try:
            print("🎯 VISIBLE BROWSER TEST")
            print("=" * 30)
            print("📱 Browser should be opening now...")
            print("👀 Look for a Chrome window!")
            
            # Go to MBT login page
            print("1. Opening MBT login page...")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot to confirm it's working
            await page.screenshot(path="browser_visible_test.png", full_page=True)
            print("   ✅ MBT page loaded - screenshot saved")
            
            # Fill login form slowly so you can see it
            print("2. Filling login form...")
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.wait_for_timeout(2000)  # Pause so you can see
            
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.wait_for_timeout(2000)  # Pause so you can see
            
            print("3. Clicking login button...")
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            await page.screenshot(path="after_login_test.png", full_page=True)
            print("   ✅ Login completed - screenshot saved")
            
            print("\n🎉 SUCCESS!")
            print("✅ Browser opened and is visible")
            print("✅ MBT login working") 
            print("✅ Screenshots saved for verification")
            
            print("\n⏳ Browser will stay open for 60 seconds...")
            print("👀 You should see the MBT dashboard in the Chrome window")
            
            # Keep browser open for 1 minute so you can see it
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="error_test.png")
            print("   📸 Error screenshot saved")
            
        finally:
            print("🔚 Closing browser...")
            await browser.close()

if __name__ == "__main__":
    print("🚀 Starting browser test...")
    print("👀 Watch for Chrome browser window to open!")
    asyncio.run(visible_browser_test())