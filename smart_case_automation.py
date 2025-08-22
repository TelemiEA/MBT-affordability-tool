"""
Smart Case Automation - Target specific case references
Use the visible case reference numbers to open pre-configured cases
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

# Case mapping from screenshot
CASE_REFERENCES = {
    "E.Single": "QX002187461",  # Single employed
    "E.Joint": "QX002187450",   # Joint employed
    "S.Single": "QX002187335",  # Single self-employed
    "S.Joint": "QX002187301"    # Joint self-employed
}

async def smart_case_automation():
    """Target specific case references and update income only."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            print("🎯 SMART CASE AUTOMATION - REFERENCE-BASED")
            print("Strategy: Target specific case reference numbers")
            print("=" * 55)
            
            # Login
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            print("✅ Login successful")
            
            # Navigate to Your Cases (we can see it's already there)
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            print("✅ Dashboard loaded")
            
            # Test with E.Single case first
            test_case = "E.Single"
            test_reference = CASE_REFERENCES[test_case]
            
            print(f"\n🎯 Testing with case: {test_case} ({test_reference})")
            
            # Click on the specific reference number
            success = await open_case_by_reference(page, test_reference)
            
            if success:
                await page.wait_for_timeout(3000)
                
                # Update income based on case type
                if test_case.startswith('E'):  # Employed case
                    await update_employed_income(page, 40000)
                else:  # Self-employed case
                    await update_self_employed_income(page, 40000, 20000)
                
                # Run the case
                await run_case_scenario(page, test_case, test_reference)
                
            else:
                print(f"❌ Could not open case: {test_case}")
                
                # Try alternative approach - look for case names directly
                print("🔄 Trying alternative approach...")
                await try_alternative_case_selection(page)
            
            # Keep browser open for inspection
            print("\n⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(120000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="smart_case_error.png")
            
        finally:
            await browser.close()


async def open_case_by_reference(page, reference_number):
    """Open a case by clicking its reference number."""
    try:
        print(f"   🔍 Looking for reference: {reference_number}")
        
        # Strategy 1: Direct click on reference text
        try:
            await page.click(f'text={reference_number}', timeout=5000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            print(f"   ✅ Opened case via reference: {reference_number}")
            await page.screenshot(path=f"opened_case_{reference_number}.png")
            return True
        except Exception as e:
            print(f"   ⚠️ Direct click failed: {e}")
        
        # Strategy 2: Look for clickable link containing the reference
        try:
            links = await page.query_selector_all('a')
            for link in links:
                try:
                    text = await link.text_content()
                    if text and reference_number in text:
                        await link.click()
                        await page.wait_for_load_state("networkidle")
                        await page.wait_for_timeout(3000)
                        print(f"   ✅ Opened case via link: {reference_number}")
                        await page.screenshot(path=f"opened_case_{reference_number}.png")
                        return True
                except:
                    continue
        except:
            pass
        
        # Strategy 3: Look in table cells
        try:
            cells = await page.query_selector_all('td')
            for cell in cells:
                try:
                    text = await cell.text_content()
                    if text and reference_number in text.strip():
                        # Check if the cell itself is clickable
                        await cell.click()
                        await page.wait_for_load_state("networkidle")
                        await page.wait_for_timeout(3000)
                        print(f"   ✅ Opened case via table cell: {reference_number}")
                        await page.screenshot(path=f"opened_case_{reference_number}.png")
                        return True
                except:
                    continue
        except:
            pass
        
        print(f"   ❌ Could not open case with reference: {reference_number}")
        return False
        
    except Exception as e:
        print(f"   ❌ Error opening case {reference_number}: {e}")
        return False


async def try_alternative_case_selection(page):
    """Try alternative approach to find and open cases."""
    try:
        print("🔄 Alternative approach: Looking for case names...")
        
        # Take screenshot to see what we're working with
        await page.screenshot(path="alternative_approach.png")
        
        # Look for any clickable elements containing our target case names
        target_cases = ["E. Single", "E. Joint", "S. Single", "S. Joint"]
        
        for case_name in target_cases:
            try:
                # Try to click on the case name
                await page.click(f'text="{case_name}"', timeout=3000)
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(3000)
                print(f"   ✅ Opened case via name: {case_name}")
                await page.screenshot(path=f"opened_via_name_{case_name.replace(' ', '_')}.png")
                return True
            except:
                continue
                
    except Exception as e:
        print(f"   ❌ Alternative approach error: {e}")
        return False


async def update_employed_income(page, salary):
    """Update employed income fields."""
    try:
        print(f"   💰 Updating employed income to £{salary:,}")
        
        # Take screenshot to see current state
        await page.screenshot(path="before_income_update.png")
        
        # Look for salary-related input fields
        input_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
        
        fields_found = 0
        for field in input_fields:
            try:
                if not await field.is_visible():
                    continue
                    
                # Get field context
                name = await field.get_attribute('name') or ''
                placeholder = await field.get_attribute('placeholder') or ''
                id_attr = await field.get_attribute('id') or ''
                
                # Get surrounding text
                parent = await field.query_selector('..')
                parent_text = ''
                if parent:
                    try:
                        parent_text = await parent.text_content() or ''
                    except:
                        pass
                
                combined_text = (name + placeholder + id_attr + parent_text).lower()
                
                # Look for salary/income keywords
                salary_keywords = ['salary', 'basic', 'annual', 'income', 'gross', 'employment']
                
                if any(keyword in combined_text for keyword in salary_keywords):
                    # Clear and fill the field
                    await field.clear()
                    await field.fill(str(salary))
                    await field.press('Tab')  # Trigger change event
                    print(f"   ✅ Updated field: {combined_text[:100]}")
                    fields_found += 1
                    
                    if fields_found >= 2:  # Limit to avoid filling too many fields
                        break
                        
            except Exception as e:
                print(f"   ⚠️ Error with field: {e}")
                continue
        
        print(f"   📊 Updated {fields_found} salary fields")
        await page.screenshot(path="after_income_update_employed.png")
        
    except Exception as e:
        print(f"   ❌ Error updating employed income: {e}")


async def update_self_employed_income(page, last_year_profit, two_year_profit):
    """Update self-employed income fields."""
    try:
        print(f"   💰 Updating self-employed income:")
        print(f"      Last year: £{last_year_profit:,}")
        print(f"      Two years: £{two_year_profit:,}")
        
        await page.screenshot(path="before_self_employed_update.png")
        
        input_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
        
        last_year_updated = False
        two_year_updated = False
        
        for field in input_fields:
            try:
                if not await field.is_visible():
                    continue
                
                # Get field context
                name = await field.get_attribute('name') or ''
                placeholder = await field.get_attribute('placeholder') or ''
                id_attr = await field.get_attribute('id') or ''
                
                # Get surrounding text
                parent = await field.query_selector('..')
                parent_text = ''
                if parent:
                    try:
                        parent_text = await parent.text_content() or ''
                    except:
                        pass
                
                combined_text = (name + placeholder + id_attr + parent_text).lower()
                
                # Look for last year profit
                if not last_year_updated and 'profit' in combined_text and ('last' in combined_text or 'current' in combined_text):
                    await field.clear()
                    await field.fill(str(last_year_profit))
                    await field.press('Tab')
                    print(f"   ✅ Updated last year profit: {combined_text[:100]}")
                    last_year_updated = True
                    continue
                
                # Look for two year profit
                if not two_year_updated and 'profit' in combined_text and ('two' in combined_text or '2' in combined_text or 'previous' in combined_text):
                    await field.clear()
                    await field.fill(str(two_year_profit))
                    await field.press('Tab')
                    print(f"   ✅ Updated two year profit: {combined_text[:100]}")
                    two_year_updated = True
                    continue
                
                if last_year_updated and two_year_updated:
                    break
                    
            except Exception as e:
                print(f"   ⚠️ Error with field: {e}")
                continue
        
        print(f"   📊 Self-employed fields updated: Last year: {last_year_updated}, Two year: {two_year_updated}")
        await page.screenshot(path="after_self_employed_update.png")
        
    except Exception as e:
        print(f"   ❌ Error updating self-employed income: {e}")


async def run_case_scenario(page, case_name, reference):
    """Run the scenario after updating income."""
    try:
        print(f"\n🚀 Running scenario for case: {case_name} ({reference})")
        
        # Look for run/submit buttons
        buttons = await page.query_selector_all('button, input[type="submit"], a')
        
        run_button_found = False
        for button in buttons:
            try:
                text = await button.text_content() or ''
                button_text = text.lower().strip()
                
                run_keywords = ['get results', 'run', 'submit', 'calculate', 'search', 'generate']
                
                if any(keyword in button_text for keyword in run_keywords):
                    print(f"   🎯 Found button: {text}")
                    await button.click()
                    await page.wait_for_load_state("networkidle")
                    await page.wait_for_timeout(5000)
                    print(f"   ✅ Clicked: {text}")
                    run_button_found = True
                    break
                    
            except:
                continue
        
        if not run_button_found:
            print("   ⚠️ No run button found")
            return
        
        # Wait for results
        print("   ⏳ Waiting for results...")
        await page.wait_for_timeout(10000)
        
        # Check for results
        page_text = await page.text_content('body')
        result_keywords = ['results', 'lender', 'quote', 'offers', 'rates']
        
        if any(keyword in page_text.lower() for keyword in result_keywords):
            print("🎉 RESULTS FOUND!")
            await page.screenshot(path=f"results_{case_name.replace('.', '_')}_{reference}.png")
            
            # Extract lender results
            target_lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom", "Newcastle", "Leeds"]
            found_lenders = [lender for lender in target_lenders if lender in page_text]
            
            if found_lenders:
                print(f"\n🎉🎉🎉 SUCCESS WITH EXISTING CASE! 🎉🎉🎉")
                print(f"📊 Case: {case_name} ({reference})")
                print(f"📈 Lenders found: {found_lenders}")
                print(f"📋 Total lenders: {len(found_lenders)}")
                print("✅ EXISTING CASE AUTOMATION SUCCESSFUL!")
                print("🚀 Ready to scale to all 32 scenarios!")
            else:
                print("✅ Reached results page")
        else:
            print("⚠️ Results not detected yet")
            await page.screenshot(path=f"waiting_for_results_{case_name.replace('.', '_')}.png")
        
    except Exception as e:
        print(f"❌ Error running scenario: {e}")


if __name__ == "__main__":
    asyncio.run(smart_case_automation())