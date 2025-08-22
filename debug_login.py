#!/usr/bin/env python3
"""
Debug MBT login issue.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def debug_login():
    """Debug the MBT login process step by step."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            print("🔍 Debugging MBT login...")
            
            # Check credentials
            username = os.getenv("MBT_USERNAME")
            password = os.getenv("MBT_PASSWORD")
            print(f"Username: {username}")
            print(f"Password: {'*' * len(password) if password else 'NOT SET'}")
            
            if not username or not password:
                print("❌ Credentials not found in environment variables!")
                return
            
            # Navigate to login page
            print("\n🌐 Navigating to login page...")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot
            await page.screenshot(path="debug_login_page.png")
            print("📸 Screenshot saved: debug_login_page.png")
            
            # Check if page loaded correctly
            title = await page.title()
            print(f"Page title: {title}")
            
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Look for login form
            print("\n🔍 Looking for login form...")
            
            email_field = await page.query_selector('input[name="email"]')
            password_field = await page.query_selector('input[name="password"]')
            submit_button = await page.query_selector('input[type="submit"]')
            
            print(f"Email field found: {email_field is not None}")
            print(f"Password field found: {password_field is not None}")
            print(f"Submit button found: {submit_button is not None}")
            
            if not email_field or not password_field:
                print("❌ Login form not found!")
                
                # Check for any error messages or redirects
                page_content = await page.content()
                if "maintenance" in page_content.lower():
                    print("🔧 Site appears to be in maintenance mode")
                elif "error" in page_content.lower():
                    print("⚠️ Error page detected")
                
                return
            
            # Fill credentials
            print("\n📝 Filling credentials...")
            await email_field.fill(username)
            await password_field.fill(password)
            
            # Take screenshot after filling
            await page.screenshot(path="debug_credentials_filled.png")
            print("📸 Screenshot saved: debug_credentials_filled.png")
            
            # Submit form
            print("\n🚀 Submitting login form...")
            await submit_button.click()
            
            # Wait for response
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(5000)
            
            # Check result
            final_url = page.url
            print(f"\n📍 Final URL: {final_url}")
            
            await page.screenshot(path="debug_after_login.png")
            print("📸 Screenshot saved: debug_after_login.png")
            
            # Check if login was successful
            if "signin" not in final_url.lower():
                print("✅ Login appears successful!")
                
                # Look for user-specific content
                user_content = await page.query_selector('text=Telemi Emmanuel-Aina')
                if user_content:
                    print("✅ User name found on page - definitely logged in!")
                
                # Look for dashboard elements
                dashboard_elements = await page.query_selector_all('.nav, .menu, [href*="dashboard"]')
                print(f"Found {len(dashboard_elements)} dashboard elements")
                
            else:
                print("❌ Login failed - still on signin page")
                
                # Look for error messages
                error_selectors = [
                    '.error', '.alert-error', '.alert-danger', 
                    '[class*="error"]', '[role="alert"]', '.text-danger'
                ]
                
                for selector in error_selectors:
                    try:
                        error_elements = await page.query_selector_all(selector)
                        for error_element in error_elements:
                            error_text = await error_element.text_content()
                            if error_text and error_text.strip():
                                print(f"❌ Error message: {error_text.strip()}")
                    except:
                        continue
            
            # Keep browser open for inspection
            print("\n⏳ Keeping browser open for 30 seconds...")
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"❌ Error during debug: {e}")
            await page.screenshot(path="debug_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_login())