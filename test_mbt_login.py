#!/usr/bin/env python3
"""
Test MBT login and explore the site structure.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def test_mbt_login():
    """Test login to MBT and explore the interface."""
    
    async with async_playwright() as p:
        # Launch browser (non-headless for debugging)
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            print("Navigating to MBT login page...")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot for debugging
            await page.screenshot(path="mbt_login_page.png")
            print("Screenshot saved: mbt_login_page.png")
            
            # Look for login form elements
            print("\nLooking for login form elements...")
            
            # Try to find email/username field
            email_selectors = [
                'input[name="email"]',
                'input[type="email"]',
                'input[id*="email"]',
                'input[placeholder*="email"]',
                'input[name="username"]',
                'input[id*="username"]'
            ]
            
            email_field = None
            for selector in email_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        print(f"Found email field: {selector}")
                        email_field = element
                        break
                except:
                    continue
            
            # Try to find password field
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                'input[id*="password"]'
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        print(f"Found password field: {selector}")
                        password_field = element
                        break
                except:
                    continue
            
            if email_field and password_field:
                print("\nAttempting to fill login form...")
                
                # Fill credentials
                await email_field.fill(os.getenv("MBT_USERNAME"))
                await password_field.fill(os.getenv("MBT_PASSWORD"))
                
                # Look for submit button
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Sign in")',
                    'button:has-text("Login")',
                    'button:has-text("Submit")',
                    '.btn-primary',
                    '[data-testid*="submit"]'
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            print(f"Found submit button: {selector}")
                            submit_button = element
                            break
                    except:
                        continue
                
                if submit_button:
                    print("Clicking submit button...")
                    await submit_button.click()
                    await page.wait_for_load_state("networkidle")
                    
                    # Wait a bit for redirect
                    await page.wait_for_timeout(3000)
                    
                    # Check current URL
                    current_url = page.url
                    print(f"Current URL after login: {current_url}")
                    
                    # Take screenshot after login
                    await page.screenshot(path="mbt_after_login.png")
                    print("Screenshot saved: mbt_after_login.png")
                    
                    # Check if we're logged in (not on signin page)
                    if "signin" not in current_url.lower():
                        print("✅ Login appears successful!")
                        
                        # Try to find navigation or menu elements
                        print("\nExploring navigation options...")
                        
                        # Look for common navigation patterns
                        nav_selectors = [
                            'nav a',
                            '.nav-link',
                            '.menu-item',
                            'a[href*="affordability"]',
                            'a[href*="calculator"]',
                            'a:has-text("Affordability")',
                            'a:has-text("Calculator")',
                            'a:has-text("Tools")'
                        ]
                        
                        nav_links = []
                        for selector in nav_selectors:
                            try:
                                elements = await page.query_selector_all(selector)
                                for element in elements:
                                    text = await element.text_content()
                                    href = await element.get_attribute('href')
                                    if text and text.strip():
                                        nav_links.append(f"{text.strip()} -> {href}")
                            except:
                                continue
                        
                        print("Found navigation links:")
                        for link in nav_links[:10]:  # Show first 10
                            print(f"  {link}")
                        
                        # Look for affordability-related content
                        page_content = await page.content()
                        affordability_keywords = ['affordability', 'calculator', 'mortgage', 'lending', 'borrowing']
                        
                        print(f"\nLooking for affordability-related content...")
                        for keyword in affordability_keywords:
                            if keyword in page_content.lower():
                                print(f"✅ Found '{keyword}' in page content")
                        
                        # Try to find any forms or calculators on the current page
                        form_elements = await page.query_selector_all('form')
                        print(f"Found {len(form_elements)} forms on page")
                        
                        input_elements = await page.query_selector_all('input')
                        print(f"Found {len(input_elements)} input elements on page")
                        
                    else:
                        print("❌ Login failed - still on signin page")
                        
                        # Check for error messages
                        error_selectors = [
                            '.error',
                            '.alert-error',
                            '.alert-danger',
                            '[class*="error"]',
                            '[role="alert"]'
                        ]
                        
                        for selector in error_selectors:
                            try:
                                error_element = await page.query_selector(selector)
                                if error_element:
                                    error_text = await error_element.text_content()
                                    print(f"Error message: {error_text}")
                            except:
                                continue
                
                else:
                    print("❌ Could not find submit button")
            
            else:
                print("❌ Could not find login form fields")
                print(f"Email field found: {email_field is not None}")
                print(f"Password field found: {password_field is not None}")
            
            # Keep browser open for manual inspection
            print("\nBrowser will remain open for 30 seconds for manual inspection...")
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"Error during login test: {e}")
            await page.screenshot(path="mbt_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_mbt_login())