"""
Manual Dropdown Completion - Final definitive approach
Manually complete the exact 2 dropdowns: Reason for Mortgage + Property Type
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def manual_dropdown_completion():
    """Manual completion of the specific dropdowns that are failing."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, 
            slow_mo=3000,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--start-maximized']
        )
        page = await browser.new_page()
        
        try:
            print("🎯 MANUAL DROPDOWN COMPLETION - FINAL APPROACH")
            print("Target: Complete Reason for Mortgage + Property Type dropdowns")
            print("=" * 65)
            
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
            
            # Take initial screenshot
            await page.screenshot(path="manual_before_dropdowns.png")
            
            # === MANUAL DROPDOWN COMPLETION ===
            print("\n🎯 MANUAL DROPDOWN COMPLETION")
            print("-" * 40)
            
            # Set Freehold first (we know this works)
            try:
                await page.click('text=Freehold')
                print("✅ Freehold set")
            except:
                pass
            
            await page.wait_for_timeout(2000)
            
            print("\n📋 PLEASE COMPLETE MANUALLY:")
            print("1. Click 'Reason for mortgage' dropdown")
            print("2. Select 'First-time buyer'")
            print("3. Click 'Property type' dropdown") 
            print("4. Select 'Terraced House'")
            print("5. Press ENTER when both are completed")
            print("\nBrowser will wait for your manual completion...")
            
            # Wait for manual completion
            print("\n⏳ Waiting for manual dropdown completion...")
            print("Press ENTER in terminal when dropdowns are completed")
            
            # Wait for user input
            input("Press ENTER when you've manually completed the dropdowns: ")
            
            print("✅ Manual completion acknowledged")
            await page.screenshot(path="manual_after_completion.png")
            
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
                        print("⚠️ Still validation errors after manual completion")
                        await page.screenshot(path="manual_still_validation.png")
                        await modal_button.click()
                        await page.wait_for_timeout(2000)
                    else:
                        print("🎉 SUCCESS! No validation errors - dropdowns completed!")
                        await page.screenshot(path="manual_success.png")
                        
                        # Continue automation
                        print("\n🔄 Continuing automated workflow...")
                        await continue_full_automation(page)
                        return
                except:
                    print("🎉 SUCCESS! No modal detected - continuing automation...")
                    await continue_full_automation(page)
                    return
            
            # If still errors, provide guidance
            print("\n📋 MANUAL COMPLETION GUIDANCE:")
            print("The dropdowns might need a specific selection technique.")
            print("Try this approach:")
            print("1. Click the dropdown arrow (right side of field)")
            print("2. Wait for dropdown to open")
            print("3. Click the specific option")
            print("4. Verify the selection appears in the field")
            
            # Keep browser open for manual work
            print("\n⏳ Keeping browser open for manual completion...")
            await page.wait_for_timeout(300000)  # 5 minutes
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="manual_error.png")
            
        finally:
            await browser.close()


async def continue_full_automation(page):
    """Continue full automation after manual dropdown completion."""
    try:
        print("🎉 DROPDOWNS COMPLETED - RESUMING AUTOMATION!")
        print("=" * 50)
        
        section_count = 0
        max_sections = 12
        
        while section_count < max_sections:
            section_count += 1
            await page.wait_for_load_state("networkidle")
            page_text = await page.text_content('body')
            current_url = page.url
            
            print(f"\nSection {section_count}: {current_url}")
            
            # Check for results
            if any(keyword in page_text.lower() for keyword in ['results', 'lender', 'quote', 'offers']):
                print("🎉 RESULTS SECTION FOUND!")
                await page.screenshot(path="MANUAL_FINAL_RESULTS.png")
                
                # Extract results
                await extract_and_display_results(page)
                return
            
            # Identify section type and fill appropriately
            if 'personal' in page_text.lower() or 'applicant' in page_text.lower():
                print("👤 Personal details section")
                await fill_personal_section(page)
                
            elif 'employment' in page_text.lower():
                print("💼 Employment section")
                await fill_employment_section(page)
                
            elif 'income' in page_text.lower():
                print("💰 Income section") 
                await fill_income_section(page)
                
            elif 'expenditure' in page_text.lower():
                print("💸 Expenditure section")
                await fill_expenditure_section(page)
                
            else:
                print("📝 Generic section")
                await fill_generic_section(page)
            
            # Submit section
            await submit_section(page, section_count)
            
            await page.wait_for_timeout(2000)
        
        print(f"⚠️ Completed {max_sections} sections")
        
    except Exception as e:
        print(f"❌ Automation continuation error: {e}")


async def fill_personal_section(page):
    """Fill personal details section."""
    try:
        # Date of birth
        date_fields = await page.query_selector_all('input[type="date"], input[name*="birth"]')
        for field in date_fields:
            try:
                if await field.is_visible():
                    await field.fill('1990-01-01')
                    print("✅ Date of birth: 01-01-1990")
                    break
            except:
                continue
        
        # Fill any dropdowns with first option
        await fill_dropdowns_with_first_option(page)
        
        # Fill number fields
        number_fields = await page.query_selector_all('input[type="number"]')
        for field in number_fields:
            try:
                if await field.is_visible():
                    name = await field.get_attribute('name') or ''
                    if 'child' in name.lower():
                        await field.fill('0')
                    else:
                        await field.fill('2')  # Joint application
            except:
                continue
                
    except Exception as e:
        print(f"⚠️ Personal section error: {e}")


async def fill_employment_section(page):
    """Fill employment section."""
    try:
        await fill_dropdowns_with_first_option(page)
        print("✅ Employment status set")
    except Exception as e:
        print(f"⚠️ Employment section error: {e}")


async def fill_income_section(page):
    """Fill income section."""
    try:
        income_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
        for field in income_fields:
            try:
                if await field.is_visible():
                    placeholder = await field.get_attribute('placeholder') or ''
                    name = await field.get_attribute('name') or ''
                    
                    if any(word in (placeholder + name).lower() for word in ['income', 'salary', 'basic', 'gross']):
                        await field.fill('40000')
                        print("✅ Income field: £40,000")
            except:
                continue
    except Exception as e:
        print(f"⚠️ Income section error: {e}")


async def fill_expenditure_section(page):
    """Fill expenditure section."""
    try:
        # Set council tax and insurance to 0
        expenditure_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
        for field in expenditure_fields:
            try:
                if await field.is_visible():
                    name = await field.get_attribute('name') or ''
                    placeholder = await field.get_attribute('placeholder') or ''
                    
                    if any(word in (name + placeholder).lower() for word in ['council', 'tax', 'insurance', 'building']):
                        await field.fill('0')
                        print("✅ Expenditure field: £0")
            except:
                continue
    except Exception as e:
        print(f"⚠️ Expenditure section error: {e}")


async def fill_generic_section(page):
    """Fill any generic section."""
    try:
        # Fill text fields
        text_fields = await page.query_selector_all('input[type="text"], input[type="email"]')
        for field in text_fields[:5]:  # Limit to avoid delays
            try:
                if await field.is_visible():
                    current_value = await field.input_value()
                    if not current_value:
                        await field.fill('Test')
            except:
                continue
        
        # Fill dropdowns
        await fill_dropdowns_with_first_option(page)
        
    except Exception as e:
        print(f"⚠️ Generic section error: {e}")


async def fill_dropdowns_with_first_option(page):
    """Fill dropdowns with first available option."""
    try:
        dropdowns = await page.query_selector_all('select')
        for dropdown in dropdowns:
            try:
                if await dropdown.is_visible():
                    options = await dropdown.query_selector_all('option')
                    if len(options) > 1:
                        await dropdown.select_option(index=1)
            except:
                continue
    except:
        pass


async def submit_section(page, section_num):
    """Submit current section."""
    try:
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
            
            print(f"✅ Section {section_num} submitted")
        else:
            print(f"⚠️ No submit button in section {section_num}")
            
    except Exception as e:
        print(f"⚠️ Submit error: {e}")


async def extract_and_display_results(page):
    """Extract and display final results."""
    try:
        print("📊 EXTRACTING FINAL RESULTS...")
        
        page_text = await page.text_content('body')
        target_lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom", "Newcastle", "Leeds"]
        found_lenders = [lender for lender in target_lenders if lender in page_text]
        
        if found_lenders:
            print(f"\n🎉🎉🎉 COMPLETE END-TO-END SUCCESS! 🎉🎉🎉")
            print("=" * 60)
            print(f"📊 LENDERS FOUND: {found_lenders}")
            print(f"📈 TOTAL LENDERS: {len(found_lenders)}")
            print("🏠 PROPERTY: Terraced House, Freehold")
            print("👥 APPLICATION: Joint")
            print("✅ MANUAL + AUTOMATED WORKFLOW COMPLETE!")
            print("=" * 60)
        else:
            print("✅ Reached results page - workflow complete!")
            
    except Exception as e:
        print(f"❌ Results extraction error: {e}")


if __name__ == "__main__":
    asyncio.run(manual_dropdown_completion())