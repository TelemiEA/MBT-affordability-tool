"""
Extract All Target Lenders - Comprehensive extraction from the affordability table
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def extract_all_target_lenders():
    """Extract all target lenders from the affordability table."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            print("🎯 COMPREHENSIVE LENDER EXTRACTION")
            print("=" * 50)
            
            # Login and setup
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            print("✅ Login successful")
            
            # Navigate to case and update income
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
            await page.click('text=QX002187461')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            print("✅ Case opened")
            
            # Quick income update
            await quick_income_update(page)
            
            # Find and extract from table
            results = await extract_complete_table(page)
            
            print(f"\n🎉 FINAL RESULTS:")
            print("=" * 30)
            for lender, amount in results.items():
                print(f"💰 {lender}: £{amount:,}")
            
            # Save results
            import json
            with open("complete_lender_extraction.json", "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to complete_lender_extraction.json")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="extraction_error.png")
            
        finally:
            print("\n⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(30000)
            await browser.close()

async def quick_income_update(page):
    """Quickly update income."""
    try:
        print("\n💰 Quick income update...")
        
        # Navigate to income section
        for attempt in range(5):
            page_text = await page.text_content('body')
            if 'annual basic salary' in page_text.lower():
                break
            
            next_buttons = await page.query_selector_all('button, input[type="submit"]')
            for button in next_buttons:
                try:
                    text = await button.text_content() or ''
                    if any(term in text.lower() for term in ['next', 'continue', 'save']):
                        await button.click()
                        await page.wait_for_load_state("networkidle")
                        await page.wait_for_timeout(2000)
                        break
                except:
                    continue
        
        # Update salary field
        inputs = await page.query_selector_all('input[type="text"], input[type="number"]')
        for input_field in inputs:
            try:
                if not await input_field.is_visible():
                    continue
                
                parent = await input_field.query_selector('..')
                if parent and 'annual basic salary' in (await parent.text_content() or '').lower():
                    await input_field.click()
                    await page.keyboard.press('Control+a')
                    await page.keyboard.press('Delete')
                    await input_field.fill('')
                    await input_field.type('35000', delay=100)
                    await input_field.press('Tab')
                    print("   ✅ Updated salary to £35,000")
                    break
            except:
                continue
                
    except Exception as e:
        print(f"   ❌ Income update error: {e}")

async def extract_complete_table(page):
    """Extract complete table data."""
    try:
        print("\n🔍 Extracting complete table data...")
        
        # Scroll to find table
        await page.evaluate("window.scrollTo(0, 500)")
        await page.wait_for_timeout(3000)
        
        # Get the table
        tables = await page.query_selector_all('table')
        
        for table in tables:
            table_text = await table.text_content()
            if 'lender' in table_text.lower() and 'affordable' in table_text.lower():
                print("   🎯 Found affordability table")
                
                return await extract_target_lenders_from_table(table)
        
        print("   ❌ No affordability table found")
        return {}
        
    except Exception as e:
        print(f"   ❌ Table extraction error: {e}")
        return {}

async def extract_target_lenders_from_table(table):
    """Extract our target lenders from the table."""
    try:
        print("   📊 Extracting target lenders...")
        
        # Define our target lenders
        target_lenders = [
            "Gen H", "Generation Home", "Accord", "Skipton", "Kensington", "Precise", 
            "Atom", "Clydesdale", "Newcastle", "Metro", "Nottingham", "Leeds", 
            "Halifax", "Santander", "Barclays", "HSBC", "Nationwide", "Coventry",
            "Principality", "Furness", "Penrith"
        ]
        
        results = {}
        
        # Get all rows
        rows = await table.query_selector_all('tr')
        print(f"   📋 Processing {len(rows)} rows...")
        
        # Skip header row, process all data rows
        for row_idx, row in enumerate(rows[1:], 1):  # Skip header
            try:
                cells = await row.query_selector_all('td, th')
                
                if len(cells) >= 3:  # Need at least lender, affordable, criteria columns
                    # Get lender name (column 1)
                    lender_cell = cells[1]
                    lender_text = await lender_cell.text_content()
                    lender_name = lender_text.strip()
                    
                    # Get affordable amount (column 2)
                    affordable_cell = cells[2]
                    affordable_text = await affordable_cell.text_content()
                    
                    # Check if this is one of our target lenders
                    for target_lender in target_lenders:
                        if target_lender.lower() in lender_name.lower():
                            # Extract amount
                            import re
                            amounts = re.findall(r'£?([\d,]+)', affordable_text)
                            if amounts:
                                try:
                                    # Get the first amount found
                                    amount_str = amounts[0].replace(',', '')
                                    amount = int(amount_str)
                                    
                                    # Validate amount is reasonable
                                    if 10000 <= amount <= 2000000:
                                        results[target_lender] = amount
                                        print(f"   💰 {target_lender}: £{amount:,} (row {row_idx})")
                                        break  # Found this target lender, move to next row
                                except ValueError:
                                    continue
                    
                    # Debug: Show all lenders we're seeing (first 20 only)
                    if row_idx <= 20:
                        print(f"   📋 Row {row_idx}: {lender_name} = {affordable_text.strip()}")
                        
            except Exception as e:
                continue
        
        print(f"   ✅ Found {len(results)} target lenders in table")
        return results
        
    except Exception as e:
        print(f"   ❌ Error extracting from table: {e}")
        return {}

if __name__ == "__main__":
    asyncio.run(extract_all_target_lenders())