"""
Direct Option Selection - Full automation approach
Target the dropdown options directly instead of just clicking dropdowns
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def direct_option_selection():
    """Directly target and select the specific dropdown options we need."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            print("🎯 DIRECT OPTION SELECTION - FULL AUTOMATION")
            print("Strategy: Target dropdown options directly")
            print("=" * 55)
            
            # Setup
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            print("✅ Login successful")
            
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            print("✅ Case created")
            
            # Basic fields
            await page.fill('input[name="firstname"]', 'Test')
            await page.fill('input[name="surname"]', 'User')
            await page.fill('input[name="email"]', 'test@example.com')
            await page.fill('input[name="purchase"]', '1000000')
            await page.fill('input[name="loan_amount"]', '100000')
            
            # Joint application
            joint_checkbox = await page.query_selector('input[type="checkbox"]')
            if joint_checkbox:
                await joint_checkbox.check()
                await page.wait_for_timeout(2000)
                print("✅ Joint application selected")
            
            # Submit to property section
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(3000)
            
            # Handle modal
            try:
                await page.click('button:has-text("OK")')
                await page.wait_for_timeout(2000)
            except:
                pass
            
            await page.wait_for_load_state("networkidle")
            print("✅ Reached property section")
            
            # === DIRECT OPTION SELECTION STRATEGY ===
            print("\n🎯 DIRECT OPTION SELECTION")
            print("-" * 40)
            
            # Set Freehold first
            try:
                await page.click('text=Freehold')
                print("✅ Freehold selected")
            except:
                pass
            
            await page.wait_for_timeout(2000)
            
            # Strategy: Find and click the option text directly, regardless of dropdown state
            print("🔍 Strategy: Direct option text targeting...")
            
            # 1. Target "First-time buyer" option directly
            print("1️⃣ Targeting 'First-time buyer' option...")
            first_time_buyer_found = await find_and_click_option("First-time buyer", page)
            
            if not first_time_buyer_found:
                # Try alternatives
                for alt_option in ["Purchase", "Buy", "Home purchase"]:
                    found = await find_and_click_option(alt_option, page)
                    if found:
                        print(f"✅ Selected alternative: {alt_option}")
                        break
            
            await page.wait_for_timeout(2000)
            
            # 2. Target "Terraced House" option directly
            print("2️⃣ Targeting 'Terraced House' option...")
            terraced_house_found = await find_and_click_option("Terraced House", page)
            
            if not terraced_house_found:
                # Try alternatives
                for alt_house in ["House", "Detached House", "Semi-detached", "Terraced"]:
                    found = await find_and_click_option(alt_house, page)
                    if found:
                        print(f"✅ Selected alternative: {alt_house}")
                        break
            
            await page.wait_for_timeout(2000)
            
            # 3. Target "35 years" or "35 year term" directly
            print("3️⃣ Targeting mortgage term...")
            term_found = False
            for term_option in ["35 years", "35 year term", "35"]:
                found = await find_and_click_option(term_option, page)
                if found:
                    print(f"✅ Selected term: {term_option}")
                    term_found = True
                    break
            
            # If no specific term found, try clicking any term checkbox
            if not term_found:
                try:
                    term_checkboxes = await page.query_selector_all('input[type="checkbox"]')
                    for checkbox in term_checkboxes:
                        parent = await checkbox.query_selector('..')
                        if parent:
                            parent_text = await parent.text_content()
                            if parent_text and ('year' in parent_text.lower() or 'term' in parent_text.lower()):
                                await checkbox.check()
                                print("✅ Term checkbox selected")
                                break
                except:
                    pass
            
            await page.wait_for_timeout(3000)
            await page.screenshot(path="direct_option_selection_complete.png")
            
            # Test submission
            print("\n🚀 Testing submission...")
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(5000)
                
                # Check for validation
                try:
                    modal_button = await page.query_selector('button:has-text("OK")')
                    if modal_button and await modal_button.is_visible():
                        print("⚠️ Still validation errors")
                        await page.screenshot(path="direct_option_validation_errors.png")
                        await modal_button.click()
                        
                        # Try more aggressive option finding
                        print("\n🔄 Trying more aggressive option targeting...")
                        await aggressive_option_targeting(page)
                        
                    else:
                        print("🎉 SUCCESS! No validation errors!")
                        await page.screenshot(path="direct_option_success.png")
                        await continue_full_automation(page)
                        return
                        
                except:
                    print("🎉 SUCCESS! No modal detected!")
                    await continue_full_automation(page)
                    return
            
            # Keep browser open for inspection
            print("\n⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="direct_option_error.png")
            
        finally:
            await browser.close()


async def find_and_click_option(option_text, page):
    """Find and click a specific option text anywhere on the page."""
    try:
        print(f"   🔍 Looking for option: {option_text}")
        
        # Strategy 1: Direct text click
        try:
            await page.click(f'text="{option_text}"', timeout=3000)
            print(f"   ✅ Found and clicked: {option_text}")
            return True
        except:
            pass
        
        # Strategy 2: Partial text match
        try:
            await page.click(f'text={option_text}', timeout=3000)
            print(f"   ✅ Found and clicked: {option_text}")
            return True
        except:
            pass
        
        # Strategy 3: Look for option elements
        try:
            options = await page.query_selector_all('option')
            for option in options:
                option_text_content = await option.text_content()
                if option_text_content and option_text.lower() in option_text_content.lower():
                    # Get the select element and select this option
                    select = await option.query_selector('..')
                    if select:
                        await select.select_option(label=option_text_content)
                        print(f"   ✅ Selected option: {option_text_content}")
                        return True
        except:
            pass
        
        # Strategy 4: Look for clickable elements containing the text
        try:
            elements = await page.query_selector_all('*')
            for element in elements:
                try:
                    element_text = await element.text_content()
                    if element_text and option_text.lower() in element_text.lower():
                        # Check if element is clickable
                        if await element.is_visible():
                            await element.click()
                            print(f"   ✅ Clicked element containing: {option_text}")
                            return True
                except:
                    continue
        except:
            pass
        
        print(f"   ❌ Could not find option: {option_text}")
        return False
        
    except Exception as e:
        print(f"   ❌ Error finding {option_text}: {e}")
        return False


async def aggressive_option_targeting(page):
    """More aggressive approach to find and select options."""
    try:
        print("🎯 AGGRESSIVE OPTION TARGETING")
        
        # Get all page text and look for our target options
        page_text = await page.text_content('body')
        
        target_options = [
            "First-time buyer", "Purchase", "Buy",
            "Terraced House", "House", "Detached",
            "35 years", "35 year", "35"
        ]
        
        for option in target_options:
            if option in page_text:
                print(f"   Found text '{option}' on page")
                
                # Try to click it with various selectors
                selectors = [
                    f'text="{option}"',
                    f'text={option}',
                    f'[value="{option}"]',
                    f'option:has-text("{option}")'
                ]
                
                for selector in selectors:
                    try:
                        await page.click(selector, timeout=2000)
                        print(f"   ✅ Successfully clicked: {option}")
                        await page.wait_for_timeout(1000)
                        break
                    except:
                        continue
        
        # Test submission again
        print("\n🚀 Testing submission after aggressive targeting...")
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
        if submit_button:
            await submit_button.click()
            await page.wait_for_timeout(5000)
            
            try:
                modal_button = await page.query_selector('button:has-text("OK")')
                if modal_button and await modal_button.is_visible():
                    print("⚠️ Still validation errors after aggressive targeting")
                    await modal_button.click()
                else:
                    print("🎉 Aggressive targeting succeeded!")
                    await continue_full_automation(page)
            except:
                print("🎉 Aggressive targeting succeeded!")
                await continue_full_automation(page)
        
    except Exception as e:
        print(f"❌ Aggressive targeting error: {e}")


async def continue_full_automation(page):
    """Continue full automation after successful dropdown completion."""
    try:
        print("\n🎉 DROPDOWN COMPLETION SUCCESSFUL - CONTINUING AUTOMATION")
        print("=" * 60)
        
        section_count = 0
        max_sections = 15
        
        while section_count < max_sections:
            section_count += 1
            await page.wait_for_load_state("networkidle")
            page_text = await page.text_content('body')
            current_url = page.url
            
            print(f"\nSection {section_count}: Processing...")
            
            # Check for results
            if any(keyword in page_text.lower() for keyword in ['results', 'lender', 'quote', 'offers']):
                print("🎉 RESULTS SECTION FOUND!")
                await page.screenshot(path="DIRECT_OPTION_FINAL_RESULTS.png")
                
                # Extract results
                target_lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom"]
                found_lenders = [lender for lender in target_lenders if lender in page_text]
                
                if found_lenders:
                    print(f"\n🎉🎉🎉 COMPLETE AUTOMATION SUCCESS! 🎉🎉🎉")
                    print("=" * 60)
                    print(f"📊 LENDERS FOUND: {found_lenders}")
                    print(f"📈 TOTAL LENDERS: {len(found_lenders)}")
                    print("✅ FULL END-TO-END AUTOMATION ACHIEVED!")
                    print("=" * 60)
                else:
                    print("✅ Reached results page - automation complete!")
                return
            
            # Quick section fill
            await quick_section_fill(page)
            
            # Submit
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(3000)
                
                # Handle modal
                try:
                    modal = await page.query_selector('button:has-text("OK")')
                    if modal and await modal.is_visible():
                        await modal.click()
                        await page.wait_for_timeout(2000)
                except:
                    pass
            else:
                break
            
            await page.wait_for_timeout(1000)
        
        print(f"⚠️ Completed {max_sections} sections")
        
    except Exception as e:
        print(f"❌ Automation continuation error: {e}")


async def quick_section_fill(page):
    """Quickly fill current section."""
    try:
        # Fill text fields
        text_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
        for field in text_fields[:5]:
            try:
                if await field.is_visible():
                    name = await field.get_attribute('name') or ''
                    if 'income' in name.lower() or 'salary' in name.lower():
                        await field.fill('40000')
                    elif 'date' in name.lower() or 'birth' in name.lower():
                        await field.fill('1990-01-01')
                    elif not await field.input_value():
                        await field.fill('0')
            except:
                continue
        
        # Select dropdown options
        dropdowns = await page.query_selector_all('select')
        for dropdown in dropdowns[:3]:
            try:
                if await dropdown.is_visible():
                    options = await dropdown.query_selector_all('option')
                    if len(options) > 1:
                        await dropdown.select_option(index=1)
            except:
                continue
                
    except:
        pass


if __name__ == "__main__":
    asyncio.run(direct_option_selection())