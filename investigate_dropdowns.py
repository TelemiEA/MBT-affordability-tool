"""
Investigate what type of dropdown elements we're actually dealing with.
The standard select approach isn't working, so let's see what we're really facing.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def investigate_dropdowns():
    """Investigate the actual dropdown implementation."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            # Setup to property section
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            
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
            
            # Submit to property section
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(3000)
            
            # Dismiss modal
            try:
                await page.click('button:has-text("OK")')
                await page.wait_for_timeout(2000)
            except:
                pass
            
            await page.wait_for_load_state("networkidle")
            
            print("🔍 Investigating dropdown elements...")
            
            # Get complete information about all form elements
            investigation_js = """
            {
                // Find all potential dropdown elements
                const allSelects = document.querySelectorAll('select');
                const allDivs = document.querySelectorAll('div[role="combobox"], div[role="listbox"], .dropdown, .select');
                const allInputs = document.querySelectorAll('input');
                const allButtons = document.querySelectorAll('button');
                
                const selectInfo = Array.from(allSelects).map((select, index) => ({
                    type: 'select',
                    index: index,
                    name: select.name || 'no-name',
                    id: select.id || 'no-id',
                    className: select.className || 'no-class',
                    placeholder: select.getAttribute('placeholder') || 'no-placeholder',
                    optionsCount: select.options.length,
                    options: Array.from(select.options).map(opt => opt.text),
                    selectedIndex: select.selectedIndex,
                    selectedValue: select.value,
                    visible: select.offsetParent !== null,
                    outerHTML: select.outerHTML.substring(0, 200)
                }));
                
                const divInfo = Array.from(allDivs).map((div, index) => ({
                    type: 'div',
                    index: index,
                    className: div.className || 'no-class',
                    textContent: div.textContent.substring(0, 100),
                    visible: div.offsetParent !== null,
                    outerHTML: div.outerHTML.substring(0, 200)
                }));
                
                // Look for elements with specific text content
                const reasonElements = Array.from(document.querySelectorAll('*')).filter(el => 
                    el.textContent && el.textContent.toLowerCase().includes('reason for mortgage')
                ).map(el => ({
                    type: 'reason-element',
                    tagName: el.tagName,
                    className: el.className || 'no-class',
                    textContent: el.textContent.substring(0, 100),
                    outerHTML: el.outerHTML.substring(0, 200)
                }));
                
                const propertyElements = Array.from(document.querySelectorAll('*')).filter(el => 
                    el.textContent && el.textContent.toLowerCase().includes('property type')
                ).map(el => ({
                    type: 'property-element',
                    tagName: el.tagName,
                    className: el.className || 'no-class',
                    textContent: el.textContent.substring(0, 100),
                    outerHTML: el.outerHTML.substring(0, 200)
                }));
                
                return {
                    selects: selectInfo,
                    divs: divInfo,
                    reasonElements: reasonElements,
                    propertyElements: propertyElements,
                    totalSelects: allSelects.length,
                    totalDivs: allDivs.length
                };
            }
            """
            
            investigation_result = await page.evaluate(investigation_js)
            
            print("📊 INVESTIGATION RESULTS:")
            print("=" * 50)
            print(f"Total select elements: {investigation_result['totalSelects']}")
            print(f"Total potential dropdown divs: {investigation_result['totalDivs']}")
            
            print("\n🔍 SELECT ELEMENTS:")
            for select in investigation_result['selects']:
                print(f"  Select {select['index']}:")
                print(f"    Name: {select['name']}")
                print(f"    Options: {select['options']}")
                print(f"    Selected: {select['selectedIndex']} ({select['selectedValue']})")
                print(f"    Visible: {select['visible']}")
                print(f"    HTML: {select['outerHTML']}")
                print()
            
            print("\n📋 REASON FOR MORTGAGE ELEMENTS:")
            for elem in investigation_result['reasonElements']:
                print(f"  {elem['tagName']}: {elem['textContent']}")
                print(f"    Class: {elem['className']}")
                print(f"    HTML: {elem['outerHTML']}")
                print()
            
            print("\n🏠 PROPERTY TYPE ELEMENTS:")
            for elem in investigation_result['propertyElements']:
                print(f"  {elem['tagName']}: {elem['textContent']}")
                print(f"    Class: {elem['className']}")
                print(f"    HTML: {elem['outerHTML']}")
                print()
            
            # Try to interact with the actual dropdown mechanism
            print("🎯 Testing actual dropdown interaction...")
            
            # Test 1: Try clicking on the dropdown area
            try:
                # Click on the "Reason for mortgage" text/area
                await page.click('text=Reason for mortgage')
                await page.wait_for_timeout(2000)
                await page.screenshot(path="after_clicking_reason_text.png")
                
                # Check if any dropdown opened
                dropdown_opened_js = """
                {
                    const openDropdowns = document.querySelectorAll('[aria-expanded="true"], .open, .dropdown-open, .show');
                    const visibleOptions = document.querySelectorAll('option:not([style*="display: none"]), .dropdown-item, .option');
                    
                    return {
                        expandedElements: openDropdowns.length,
                        visibleOptions: visibleOptions.length,
                        expandedHTML: Array.from(openDropdowns).map(el => el.outerHTML.substring(0, 100))
                    };
                }
                """
                
                dropdown_state = await page.evaluate(dropdown_opened_js)
                print(f"After clicking reason text: {dropdown_state}")
                
            except Exception as e:
                print(f"Error clicking reason text: {e}")
            
            # Test 2: Try clicking directly on select elements
            try:
                select_elements = await page.query_selector_all('select')
                print(f"Found {len(select_elements)} select elements to test")
                
                for i, select in enumerate(select_elements):
                    try:
                        print(f"Testing select element {i}...")
                        await select.click()
                        await page.wait_for_timeout(1000)
                        
                        # Try to select by value
                        await select.select_option(index=1)
                        await page.wait_for_timeout(1000)
                        
                        print(f"  ✅ Select {i} interacted successfully")
                        
                    except Exception as e:
                        print(f"  ❌ Select {i} error: {e}")
                
                await page.screenshot(path="after_select_interaction.png")
                
            except Exception as e:
                print(f"Error with select interaction: {e}")
            
            # Keep browser open for manual testing
            print("\n⏳ Keeping browser open for manual testing...")
            print("You can now manually interact with the dropdowns to see how they work")
            await page.wait_for_timeout(180000)  # 3 minutes
            
        except Exception as e:
            print(f"❌ Investigation error: {e}")
            await page.screenshot(path="investigation_error.png")
            
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(investigate_dropdowns())