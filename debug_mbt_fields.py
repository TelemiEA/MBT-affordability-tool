#!/usr/bin/env python3
"""
Debug MBT form fields to understand exact selectors needed.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def debug_mbt_fields():
    """Debug exact form fields in MBT."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            # Login
            print("🔐 Logging in...")
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            # Start new case
            print("📝 Starting new case...")
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)
            
            # Debug first page fields
            print("\n🔍 Analyzing first page fields...")
            
            # Get all input elements
            inputs = await page.query_selector_all('input')
            print(f"Found {len(inputs)} input elements:")
            
            for i, input_elem in enumerate(inputs[:20]):  # First 20 inputs
                try:
                    name = await input_elem.get_attribute('name')
                    id_attr = await input_elem.get_attribute('id')
                    type_attr = await input_elem.get_attribute('type')
                    placeholder = await input_elem.get_attribute('placeholder')
                    
                    print(f"  Input {i+1}:")
                    print(f"    Name: {name}")
                    print(f"    ID: {id_attr}")
                    print(f"    Type: {type_attr}")
                    print(f"    Placeholder: {placeholder}")
                    print()
                except Exception as e:
                    print(f"  Input {i+1}: Error getting attributes - {e}")
            
            # Try to fill visible fields
            print("🖊️  Trying to fill visible text fields...")
            
            text_inputs = await page.query_selector_all('input[type="text"], input:not([type])')
            for i, input_elem in enumerate(text_inputs[:5]):
                try:
                    if await input_elem.is_visible():
                        name = await input_elem.get_attribute('name')
                        id_attr = await input_elem.get_attribute('id')
                        print(f"Filling visible input: name={name}, id={id_attr}")
                        
                        if 'first' in str(name).lower() or 'first' in str(id_attr).lower():
                            await input_elem.fill('John')
                        elif 'surname' in str(name).lower() or 'last' in str(name).lower():
                            await input_elem.fill('Doe')
                        elif 'email' in str(name).lower():
                            await input_elem.fill('john.doe@test.com')
                        else:
                            await input_elem.fill('Test')
                        
                        print(f"✅ Successfully filled {name or id_attr}")
                except Exception as e:
                    print(f"❌ Error filling input: {e}")
            
            await page.screenshot(path="debug_first_page_filled.png")
            
            # Try to proceed to next step
            print("\n➡️  Looking for Next/Submit button...")
            
            buttons = await page.query_selector_all('button, input[type="submit"]')
            print(f"Found {len(buttons)} buttons:")
            
            for i, button in enumerate(buttons):
                try:
                    text = await button.text_content()
                    type_attr = await button.get_attribute('type')
                    name = await button.get_attribute('name')
                    
                    print(f"  Button {i+1}: text='{text}', type='{type_attr}', name='{name}'")
                    
                    if await button.is_visible() and (
                        'submit' in str(type_attr).lower() or 
                        'next' in str(text).lower() or
                        'continue' in str(text).lower()
                    ):
                        print(f"Clicking button: {text or type_attr}")
                        await button.click()
                        await page.wait_for_timeout(3000)
                        break
                        
                except Exception as e:
                    print(f"  Button {i+1}: Error - {e}")
            
            await page.screenshot(path="debug_second_page.png")
            
            # Analyze second page
            print("\n🔍 Analyzing second page...")
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Look for any error messages or validation issues
            error_elements = await page.query_selector_all('.error, .alert, [class*="error"], [role="alert"]')
            if error_elements:
                print("⚠️  Found error/alert elements:")
                for error in error_elements:
                    text = await error.text_content()
                    if text:
                        print(f"  Error: {text}")
            
            # Check for modal dialogs
            modals = await page.query_selector_all('.modal, [role="dialog"]')
            if modals:
                print("📱 Found modal dialogs:")
                for modal in modals:
                    text = await modal.text_content()
                    if text:
                        print(f"  Modal: {text[:100]}...")
                        
                    # Try to close modal
                    ok_button = await modal.query_selector('button:has-text("OK"), button:has-text("Close")')
                    if ok_button:
                        await ok_button.click()
                        await page.wait_for_timeout(1000)
            
            # Look for dropdowns that need to be filled
            selects = await page.query_selector_all('select')
            print(f"\nFound {len(selects)} dropdown fields:")
            
            for i, select in enumerate(selects):
                try:
                    name = await select.get_attribute('name')
                    id_attr = await select.get_attribute('id')
                    
                    # Get options
                    options = await select.query_selector_all('option')
                    option_texts = []
                    for option in options[:5]:  # First 5 options
                        text = await option.text_content()
                        value = await option.get_attribute('value')
                        option_texts.append(f"{text} (value: {value})")
                    
                    print(f"  Select {i+1}: name={name}, id={id_attr}")
                    print(f"    Options: {option_texts}")
                    
                    # Try to select a reasonable option
                    if await select.is_visible() and options:
                        if 'reason' in str(name).lower():
                            await select.select_option('First Time Buyer')
                        elif len(options) > 1:
                            await select.select_option(index=1)  # Select second option
                        print(f"    ✅ Selected option")
                        
                except Exception as e:
                    print(f"  Select {i+1}: Error - {e}")
            
            await page.screenshot(path="debug_dropdowns_filled.png")
            
            print("\n⏳ Keeping browser open for manual inspection...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error during debugging: {e}")
            await page.screenshot(path="debug_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_mbt_fields())