#!/usr/bin/env python3
"""
Test MBT navigation to find affordability calculator.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def test_mbt_navigation():
    """Test navigation to affordability calculator in MBT."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            # Login first
            print("Logging into MBT...")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            print("✅ Login successful!")
            
            # Now explore the interface for affordability tools
            print("\nExploring affordability options...")
            
            # Look for "Create RESI Case" which might lead to affordability
            try:
                create_resi = await page.query_selector('text=Create RESI Case')
                if create_resi:
                    print("Found 'Create RESI Case' - clicking...")
                    await create_resi.click()
                    await page.wait_for_load_state("networkidle")
                    await page.wait_for_timeout(2000)
                    
                    await page.screenshot(path="mbt_resi_case.png")
                    print("Screenshot saved: mbt_resi_case.png")
                    
                    current_url = page.url
                    print(f"Current URL: {current_url}")
                    
                    # Look for affordability-related elements
                    affordability_elements = await page.query_selector_all('text=/affordability/i')
                    print(f"Found {len(affordability_elements)} affordability-related elements")
                    
                    # Look for forms or input fields
                    input_fields = await page.query_selector_all('input')
                    print(f"Found {len(input_fields)} input fields")
                    
                    # Check page content for affordability terms
                    page_content = await page.content()
                    
                    affordability_keywords = [
                        'affordability', 'income', 'borrowing', 'calculation', 
                        'mortgage amount', 'salary', 'employment'
                    ]
                    
                    found_keywords = []
                    for keyword in affordability_keywords:
                        if keyword.lower() in page_content.lower():
                            found_keywords.append(keyword)
                    
                    print(f"Found keywords in page: {found_keywords}")
                    
                    # Look for specific form fields that might be for affordability
                    income_selectors = [
                        'input[name*="income"]',
                        'input[id*="income"]',
                        'input[placeholder*="income"]',
                        'input[name*="salary"]',
                        'input[id*="salary"]'
                    ]
                    
                    income_fields = []
                    for selector in income_selectors:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            income_fields.extend(elements)
                    
                    print(f"Found {len(income_fields)} potential income fields")
                    
                    # Try to find navigation tabs or steps
                    tab_selectors = [
                        '[role="tab"]',
                        '.tab',
                        '.nav-tab',
                        'a[href*="affordability"]',
                        'button:has-text("Affordability")',
                        'a:has-text("Affordability")'
                    ]
                    
                    for selector in tab_selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            for element in elements:
                                text = await element.text_content()
                                if text and 'affordability' in text.lower():
                                    print(f"Found affordability tab/link: {text}")
                                    
                                    # Try clicking it
                                    try:
                                        await element.click()
                                        await page.wait_for_timeout(2000)
                                        await page.screenshot(path="mbt_affordability_clicked.png")
                                        print("Clicked affordability element - screenshot saved")
                                        break
                                    except:
                                        continue
                        except:
                            continue
                    
                    # Look for any calculation or submit buttons
                    calc_buttons = await page.query_selector_all('button:has-text("Calculate"), button:has-text("Run"), button:has-text("Check")')
                    print(f"Found {len(calc_buttons)} potential calculation buttons")
                    
                    for button in calc_buttons:
                        text = await button.text_content()
                        print(f"  Button: {text}")
            
            except Exception as e:
                print(f"Error with Create RESI Case: {e}")
            
            # Try alternative navigation paths
            print("\nTrying alternative navigation...")
            
            # Look for direct affordability links
            affordability_links = await page.query_selector_all('a:has-text("Affordability")')
            if affordability_links:
                print("Found direct affordability links!")
                for link in affordability_links:
                    href = await link.get_attribute('href')
                    text = await link.text_content()
                    print(f"  {text} -> {href}")
            
            # Try navigating to common affordability URLs
            common_affordability_paths = [
                '/affordability',
                '/calculator',
                '/tools/affordability',
                '/dashboard/affordability'
            ]
            
            base_url = page.url.split('/dashboard')[0] if '/dashboard' in page.url else page.url
            
            for path in common_affordability_paths:
                try:
                    test_url = base_url + path
                    print(f"Trying URL: {test_url}")
                    
                    await page.goto(test_url)
                    await page.wait_for_timeout(2000)
                    
                    if page.url == test_url:
                        print(f"✅ Successfully navigated to {test_url}")
                        await page.screenshot(path=f"mbt_path_{path.replace('/', '_')}.png")
                        
                        # Check if this looks like an affordability page
                        content = await page.content()
                        if any(keyword in content.lower() for keyword in ['affordability', 'income', 'borrowing']):
                            print("This page contains affordability-related content!")
                            break
                    else:
                        print(f"Redirected from {test_url} to {page.url}")
                
                except Exception as e:
                    print(f"Error trying {path}: {e}")
            
            print("\nKeeping browser open for 30 seconds for manual exploration...")
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"Error during navigation test: {e}")
            await page.screenshot(path="mbt_navigation_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_mbt_navigation())