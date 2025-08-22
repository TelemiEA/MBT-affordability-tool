"""
Test Table Identification - Focus on finding the affordability results table
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def test_table_identification():
    """Test finding and reading the affordability results table."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            print("🔍 TABLE IDENTIFICATION TEST")
            print("=" * 50)
            
            # Login and navigate to case
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            print("✅ Login successful")
            
            # Navigate to case
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
            # Open E.Single case
            await page.click('text=QX002187461')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            print("✅ Case opened")
            
            # Navigate to income section and update income
            await navigate_to_income_and_update(page)
            
            # Now the critical part - find the table after results are shown
            await find_and_identify_table(page)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="table_identification_error.png")
            
        finally:
            print("\n⏳ Keeping browser open for manual inspection...")
            await page.wait_for_timeout(60000)
            await browser.close()

async def navigate_to_income_and_update(page):
    """Navigate to income section and update income."""
    try:
        print("\n🧭 Navigating to income section...")
        
        # Navigate through form sections until we reach income
        for attempt in range(5):
            page_text = await page.text_content('body')
            
            if any(term in page_text.lower() for term in ['annual basic salary', 'net profit', 'income']):
                print("   ✅ Reached income section")
                break
            
            # Look for Next/Continue buttons
            next_buttons = await page.query_selector_all('button, input[type="submit"]')
            for button in next_buttons:
                try:
                    text = await button.text_content() or ''
                    if any(term in text.lower() for term in ['next', 'continue', 'save']):
                        await button.click()
                        await page.wait_for_load_state("networkidle")
                        await page.wait_for_timeout(2000)
                        print(f"   ✅ Clicked: {text}")
                        break
                except:
                    continue
        
        # Update income to £30,000
        print("\n💰 Updating income to £30,000...")
        inputs = await page.query_selector_all('input[type="text"], input[type="number"]')
        
        for input_field in inputs:
            try:
                if not await input_field.is_visible():
                    continue
                
                parent = await input_field.query_selector('..')
                if parent:
                    parent_text = await parent.text_content() or ''
                    
                    if 'annual basic salary' in parent_text.lower():
                        # Clear field completely
                        await input_field.click()
                        await page.keyboard.press('Control+a')
                        await page.keyboard.press('Delete')
                        await input_field.fill('')
                        await page.wait_for_timeout(500)
                        
                        # Enter new amount
                        await input_field.type('30000', delay=100)
                        await input_field.press('Tab')
                        
                        print("   ✅ Updated salary to £30,000")
                        break
            except:
                continue
                
    except Exception as e:
        print(f"   ❌ Error updating income: {e}")

async def find_and_identify_table(page):
    """Find and identify the affordability results table."""
    try:
        print("\n🎯 SEARCHING FOR AFFORDABILITY TABLE")
        print("=" * 40)
        
        # Step 1: Look for green button and click it
        print("1. Looking for green button to trigger results...")
        
        green_selectors = [
            'button:has(i.zmdi-play)',
            'i.zmdi-play', 
            '.btn-success',
            'button[class*="play"]'
        ]
        
        button_clicked = False
        for selector in green_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    print(f"   🎯 Found green button: {selector}")
                    await element.click()
                    await page.wait_for_load_state("networkidle", timeout=30000)
                    await page.wait_for_timeout(5000)
                    print(f"   ✅ Clicked green button")
                    button_clicked = True
                    break
            except Exception as e:
                print(f"   ⚠️ Failed {selector}: {e}")
                continue
        
        if not button_clicked:
            print("   ⚠️ No green button found - proceeding to look for existing results")
        
        # Step 2: Scroll down gradually to find the table
        print("\n2. Scrolling down gradually to find results table...")
        
        for scroll_step in range(20):  # Try 20 scroll steps
            print(f"   📍 Scroll step {scroll_step + 1}")
            
            # Scroll down by 300px each step
            scroll_position = scroll_step * 300
            await page.evaluate(f"window.scrollTo(0, {scroll_position})")
            await page.wait_for_timeout(1500)
            
            # Take screenshot at each step
            await page.screenshot(path=f"scroll_step_{scroll_step + 1:02d}.png")
            
            # Check for table indicators
            page_text = await page.text_content('body')
            
            # Look for affordability table indicators
            table_indicators = [
                'lender' in page_text.lower() and 'affordable' in page_text.lower(),
                'criteria' in page_text.lower() and 'affordable' in page_text.lower(),
                '£' in page_text and 'lender' in page_text.lower(),
                'best buy' in page_text.lower() and 'affordable' in page_text.lower()
            ]
            
            if any(table_indicators):
                print(f"   🎯 Found table indicators at scroll step {scroll_step + 1}")
                
                # Analyze the table at this position
                await analyze_tables_at_position(page, scroll_step + 1)
                
                # Don't break - continue scrolling to see if there are more tables
        
        # Final scroll to bottom
        print("\n3. Final scroll to bottom...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="final_bottom_position.png")
        
        # Final table analysis
        await analyze_tables_at_position(page, "final")
        
    except Exception as e:
        print(f"❌ Error finding table: {e}")

async def analyze_tables_at_position(page, position):
    """Analyze all tables at current scroll position."""
    try:
        print(f"\n   📊 ANALYZING TABLES AT POSITION {position}")
        
        # Get all tables
        tables = await page.query_selector_all('table')
        print(f"   📋 Found {len(tables)} tables at this position")
        
        for table_idx, table in enumerate(tables):
            try:
                table_text = await table.text_content()
                
                # Check if this looks like the affordability table
                is_affordability_table = (
                    'lender' in table_text.lower() and 
                    'affordable' in table_text.lower()
                )
                
                if is_affordability_table:
                    print(f"\n   🎯 FOUND AFFORDABILITY TABLE {table_idx + 1}!")
                    print(f"   📝 Table text preview: {table_text[:200]}...")
                    
                    # Get table structure
                    rows = await table.query_selector_all('tr')
                    print(f"   📊 Table has {len(rows)} rows")
                    
                    # Analyze header row
                    if rows:
                        header_row = rows[0]
                        headers = await header_row.query_selector_all('th, td')
                        print(f"   📋 Header row has {len(headers)} columns:")
                        
                        for col_idx, header in enumerate(headers):
                            header_text = await header.text_content()
                            print(f"      Column {col_idx}: '{header_text.strip()}'")
                    
                    # Try to extract some sample data
                    await extract_sample_data(table, table_idx + 1)
                else:
                    print(f"   📋 Table {table_idx + 1}: Not affordability table")
                    
            except Exception as e:
                print(f"   ⚠️ Error analyzing table {table_idx + 1}: {e}")
                
    except Exception as e:
        print(f"   ❌ Error in table analysis: {e}")

async def extract_sample_data(table, table_number):
    """Extract sample data from the affordability table."""
    try:
        print(f"\n   💰 EXTRACTING SAMPLE DATA FROM TABLE {table_number}")
        
        rows = await table.query_selector_all('tr')
        
        # Find column positions
        if not rows:
            print("   ⚠️ No rows found")
            return
            
        header_row = rows[0]
        headers = await header_row.query_selector_all('th, td')
        
        lender_col = -1
        affordable_col = -1
        
        for col_idx, header in enumerate(headers):
            header_text = await header.text_content()
            if 'lender' in header_text.lower():
                lender_col = col_idx
                print(f"   🏦 Lender column: {col_idx}")
            if 'affordable' in header_text.lower():
                affordable_col = col_idx
                print(f"   💰 Affordable column: {col_idx}")
        
        if lender_col >= 0 and affordable_col >= 0:
            print(f"   🎯 Extracting data from rows...")
            
            sample_count = 0
            for row_idx, row in enumerate(rows[1:5]):  # Sample first 4 data rows
                try:
                    cells = await row.query_selector_all('td, th')
                    
                    if len(cells) > max(lender_col, affordable_col):
                        lender_text = await cells[lender_col].text_content()
                        affordable_text = await cells[affordable_col].text_content()
                        
                        print(f"   📋 Row {row_idx + 1}: {lender_text.strip()} = {affordable_text.strip()}")
                        sample_count += 1
                        
                except Exception as e:
                    continue
            
            print(f"   ✅ Successfully extracted {sample_count} sample rows")
        else:
            print("   ❌ Could not identify lender or affordable columns")
            
    except Exception as e:
        print(f"   ❌ Error extracting sample data: {e}")

if __name__ == "__main__":
    asyncio.run(test_table_identification())