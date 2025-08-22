"""
Debug the form structure of credit commitment cases
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def debug_credit_case_form():
    """Debug the form structure in a credit case."""
    
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
        
        # Open the credit case
        print("🎯 Opening C . E-Single case...")
        await page.click('text=C . E-Single', timeout=10000)
        await page.wait_for_load_state("networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        print("✅ Opened credit case")
        
        # Take screenshot of initial state
        await page.screenshot(path="credit_case_initial.png", full_page=True)
        print("📷 Screenshot 1: credit_case_initial.png")
        
        # Get all input fields
        inputs = await page.query_selector_all('input[type="text"], input[type="number"]')
        print(f"\n🔍 Found {len(inputs)} input fields")
        
        input_info = []
        for i, input_field in enumerate(inputs[:20]):  # Check first 20 inputs
            try:
                if await input_field.is_visible():
                    # Get parent context
                    parent = await input_field.query_selector('..')
                    if parent:
                        parent_text = await parent.text_content()
                        if parent_text:
                            cleaned_text = ' '.join(parent_text.strip().split())[:100]  # Clean and limit
                            input_info.append(f"Input {i+1}: {cleaned_text}")
            except:
                continue
        
        print("📋 Visible input field contexts:")
        for info in input_info[:10]:  # Show first 10
            print(f"   {info}")
        
        # Look for specific income-related terms
        page_text = await page.text_content('body')
        income_terms = ['annual basic salary', 'salary', 'income', 'earnings', 'net profit', 'employed', 'self-employed']
        found_terms = []
        for term in income_terms:
            if term.lower() in page_text.lower():
                found_terms.append(term)
        
        if found_terms:
            print(f"\n📋 Income-related terms found: {found_terms}")
        
        # Try to navigate through sections
        print("\n🔄 Looking for navigation buttons...")
        buttons = await page.query_selector_all('button, input[type="submit"], a')
        nav_buttons = []
        for button in buttons[:20]:
            try:
                button_text = await button.text_content()
                if button_text and any(term in button_text.lower() for term in ['next', 'continue', 'save', 'section', 'step']):
                    nav_buttons.append(button_text.strip())
            except:
                continue
        
        if nav_buttons:
            print(f"📋 Navigation buttons found: {nav_buttons}")
            
            # Try clicking the first next/continue button
            if nav_buttons:
                try:
                    first_button = nav_buttons[0]
                    await page.click(f'text={first_button}', timeout=5000)
                    await page.wait_for_load_state("networkidle", timeout=10000)
                    await page.wait_for_timeout(2000)
                    print(f"✅ Clicked: {first_button}")
                    
                    # Take another screenshot
                    await page.screenshot(path="credit_case_after_nav.png", full_page=True)
                    print("📷 Screenshot 2: credit_case_after_nav.png")
                except Exception as e:
                    print(f"⚠️ Could not click button: {e}")
        
        print(f"\n🔍 Waiting 15 seconds for manual inspection...")
        await page.wait_for_timeout(15000)
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
    
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(debug_credit_case_form())