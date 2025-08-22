"""
Existing Case Automation - Use pre-configured cases and update income only
Smart approach: Open existing cases and modify just the income fields
Cases: E.Single, E.Joint, S.Single, S.Joint
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def existing_case_automation():
    """Use existing pre-configured cases and update income fields only."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        page = await browser.new_page()
        
        try:
            print("🎯 EXISTING CASE AUTOMATION - SMART APPROACH")
            print("Strategy: Use pre-configured cases, update income only")
            print("=" * 60)
            
            # Login
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            print("✅ Login successful")
            
            # Go to dashboard
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
            # Take screenshot of dashboard
            await page.screenshot(path="dashboard_cases.png")
            print("✅ Dashboard loaded")
            
            # Look for existing cases on main dashboard
            print("\n🔍 Looking for existing cases...")
            page_text = await page.text_content('body')
            
            # Check if we can see the cases directly
            target_cases = ["E.Single", "E.Joint", "S.Single", "S.Joint"]
            visible_cases = []
            
            for case in target_cases:
                if case in page_text:
                    visible_cases.append(case)
                    print(f"   ✅ Found case: {case}")
            
            # If no cases visible on main dashboard, try "Your Cases" sidebar
            if not visible_cases:
                print("\n📁 Cases not visible on dashboard, trying 'Your Cases' sidebar...")
                try:
                    await page.click('text=Your Cases')
                    await page.wait_for_load_state("networkidle")
                    await page.wait_for_timeout(3000)
                    
                    await page.screenshot(path="your_cases_panel.png")
                    
                    # Check again for cases
                    page_text = await page.text_content('body')
                    for case in target_cases:
                        if case in page_text:
                            visible_cases.append(case)
                            print(f"   ✅ Found case in sidebar: {case}")
                            
                except Exception as e:
                    print(f"   ⚠️ Could not access Your Cases sidebar: {e}")
            
            if visible_cases:
                print(f"\n📊 Found {len(visible_cases)} existing cases: {visible_cases}")
                
                # Test with first available case
                test_case = visible_cases[0]
                print(f"\n🎯 Testing with case: {test_case}")
                
                # Try to click on the case to open it
                success = await open_case(page, test_case)
                
                if success:
                    # Determine income fields based on case type
                    if test_case.startswith('E'):  # Employed case
                        await update_employed_income(page, 40000)
                    else:  # Self-employed case
                        await update_self_employed_income(page, 40000, 20000)
                    
                    # Run the case
                    await run_case_scenario(page, test_case)
                    
                else:
                    print("❌ Could not open the case")
                    
            else:
                print("❌ No target cases found")
                print("Available text on page:")
                print(page_text[:500] + "..." if len(page_text) > 500 else page_text)
            
            # Keep browser open for inspection
            print("\n⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="existing_case_error.png")
            
        finally:
            await browser.close()


async def open_case(page, case_name):
    """Try to open a specific case by clicking on its reference."""
    try:
        print(f"   🔍 Looking for case reference: {case_name}")
        
        # Strategy 1: Direct text click
        try:
            await page.click(f'text={case_name}', timeout=5000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            print(f"   ✅ Opened case: {case_name}")
            await page.screenshot(path=f"opened_case_{case_name.replace('.', '_')}.png")
            return True
        except:
            pass
        
        # Strategy 2: Look for clickable elements containing the case name
        try:
            elements = await page.query_selector_all('a, button, div[onclick], span[onclick]')
            for element in elements:
                try:
                    text = await element.text_content()
                    if text and case_name in text:
                        await element.click()
                        await page.wait_for_load_state("networkidle")
                        await page.wait_for_timeout(3000)
                        print(f"   ✅ Opened case via element: {case_name}")
                        await page.screenshot(path=f"opened_case_{case_name.replace('.', '_')}.png")
                        return True
                except:
                    continue
        except:
            pass
        
        # Strategy 3: Look for table rows or list items
        try:
            rows = await page.query_selector_all('tr, li, .case-item, .row')
            for row in rows:
                try:
                    text = await row.text_content()
                    if text and case_name in text:
                        # Look for clickable elements within the row
                        clickable = await row.query_selector('a, button')
                        if clickable:
                            await clickable.click()
                        else:
                            await row.click()
                        await page.wait_for_load_state("networkidle")
                        await page.wait_for_timeout(3000)
                        print(f"   ✅ Opened case via row: {case_name}")
                        await page.screenshot(path=f"opened_case_{case_name.replace('.', '_')}.png")
                        return True
                except:
                    continue
        except:
            pass
        
        print(f"   ❌ Could not open case: {case_name}")
        return False
        
    except Exception as e:
        print(f"   ❌ Error opening case {case_name}: {e}")
        return False


async def update_employed_income(page, salary):
    """Update employed income fields."""
    try:
        print(f"   💰 Updating employed income to £{salary:,}")
        
        # Look for "annual basic salary" field
        salary_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
        
        for field in salary_fields:
            try:
                # Check field attributes for salary-related terms
                name = await field.get_attribute('name') or ''
                placeholder = await field.get_attribute('placeholder') or ''
                label_text = ''
                
                # Try to get associated label
                try:
                    parent = await field.query_selector('..')
                    if parent:
                        label_text = await parent.text_content() or ''
                except:
                    pass
                
                combined_text = (name + placeholder + label_text).lower()
                
                if any(term in combined_text for term in ['salary', 'basic', 'annual', 'income']):
                    if await field.is_visible():
                        await field.clear()
                        await field.fill(str(salary))
                        print(f"   ✅ Updated salary field: {combined_text[:50]}")
                        break
                        
            except:
                continue
                
        await page.screenshot(path="income_updated_employed.png")
        
    except Exception as e:
        print(f"   ❌ Error updating employed income: {e}")


async def update_self_employed_income(page, last_year_profit, two_year_profit):
    """Update self-employed income fields."""
    try:
        print(f"   💰 Updating self-employed income:")
        print(f"      Last year: £{last_year_profit:,}")
        print(f"      Two years: £{two_year_profit:,}")
        
        # Look for net profit fields
        income_fields = await page.query_selector_all('input[type="text"], input[type="number"]')
        
        fields_updated = 0
        
        for field in income_fields:
            try:
                name = await field.get_attribute('name') or ''
                placeholder = await field.get_attribute('placeholder') or ''
                label_text = ''
                
                # Try to get associated label
                try:
                    parent = await field.query_selector('..')
                    if parent:
                        label_text = await parent.text_content() or ''
                except:
                    pass
                
                combined_text = (name + placeholder + label_text).lower()
                
                # Check for last year profit field
                if 'last' in combined_text and 'profit' in combined_text:
                    if await field.is_visible():
                        await field.clear()
                        await field.fill(str(last_year_profit))
                        print(f"   ✅ Updated last year profit: {combined_text[:50]}")
                        fields_updated += 1
                        continue
                
                # Check for two year profit field
                if ('two' in combined_text or '2' in combined_text) and 'profit' in combined_text:
                    if await field.is_visible():
                        await field.clear()
                        await field.fill(str(two_year_profit))
                        print(f"   ✅ Updated two year profit: {combined_text[:50]}")
                        fields_updated += 1
                        continue
                        
            except:
                continue
        
        print(f"   📊 Updated {fields_updated} self-employed income fields")
        await page.screenshot(path="income_updated_self_employed.png")
        
    except Exception as e:
        print(f"   ❌ Error updating self-employed income: {e}")


async def run_case_scenario(page, case_name):
    """Run the scenario after updating income."""
    try:
        print(f"\n🚀 Running scenario for case: {case_name}")
        
        # Look for run/submit/calculate button
        buttons = await page.query_selector_all('button, input[type="submit"]')
        
        for button in buttons:
            try:
                text = await button.text_content() or ''
                button_text = text.lower()
                
                if any(term in button_text for term in ['run', 'submit', 'calculate', 'get results', 'search']):
                    await button.click()
                    await page.wait_for_load_state("networkidle")
                    await page.wait_for_timeout(5000)
                    print(f"   ✅ Clicked: {text}")
                    break
                    
            except:
                continue
        
        # Wait for results
        await page.wait_for_timeout(10000)
        
        # Check for results
        page_text = await page.text_content('body')
        if any(keyword in page_text.lower() for keyword in ['results', 'lender', 'quote', 'offers']):
            print("🎉 RESULTS FOUND!")
            await page.screenshot(path=f"results_{case_name.replace('.', '_')}.png")
            
            # Extract lender results
            target_lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom"]
            found_lenders = [lender for lender in target_lenders if lender in page_text]
            
            if found_lenders:
                print(f"\n🎉🎉🎉 SUCCESS WITH EXISTING CASE! 🎉🎉🎉")
                print(f"📊 Case: {case_name}")
                print(f"📈 Lenders found: {found_lenders}")
                print(f"📋 Total lenders: {len(found_lenders)}")
                print("✅ EXISTING CASE AUTOMATION WORKS!")
            else:
                print("✅ Reached results page")
        else:
            print("⚠️ Results not found yet")
            await page.screenshot(path=f"no_results_{case_name.replace('.', '_')}.png")
        
    except Exception as e:
        print(f"❌ Error running scenario: {e}")


if __name__ == "__main__":
    asyncio.run(existing_case_automation())