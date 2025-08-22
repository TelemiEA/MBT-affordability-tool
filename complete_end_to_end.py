"""
Complete end-to-end MBT automation using direct JavaScript execution 
to handle the final dropdowns and complete the full workflow.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv
import re

load_dotenv()

class MBTEndToEndAutomation:
    """Complete end-to-end MBT automation."""
    
    def __init__(self):
        self.username = os.getenv("MBT_USERNAME")
        self.password = os.getenv("MBT_PASSWORD")
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        self.target_lenders = [
            "Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom",
            "Clydesdale", "Newcastle", "Metro", "Nottingham", "Hinckley & Rugby",
            "Leeds", "Principality", "Coventry", "Santander"
        ]
    
    async def start_browser(self, headless: bool = False):
        """Start browser."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-dev-shm-usage'],
            slow_mo=1000
        )
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
    
    async def login(self) -> bool:
        """Login to MBT."""
        try:
            print("🔐 Logging into MBT...")
            await self.page.goto("https://mortgagebrokertools.co.uk/signin", wait_until='networkidle')
            await self.page.wait_for_timeout(2000)
            
            await self.page.fill('input[name="email"]', self.username)
            await self.page.fill('input[name="password"]', self.password)
            await self.page.click('input[type="submit"]')
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            await self.page.wait_for_timeout(3000)
            
            if "signin" not in self.page.url.lower():
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login failed")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    async def create_new_case(self, scenario: Dict) -> bool:
        """Create a new RESI case."""
        try:
            print(f"📝 Creating NEW case for {scenario['scenario_id']}...")
            
            await self.page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await self.page.wait_for_load_state("networkidle")
            await self.page.wait_for_timeout(2000)
            
            await self.page.click('text=Create RESI Case')
            await self.page.wait_for_load_state("networkidle")
            await self.page.wait_for_timeout(3000)
            
            print(f"✅ New case created: {self.page.url}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating case: {e}")
            return False
    
    async def dismiss_modals(self) -> bool:
        """Dismiss any modal dialogs."""
        try:
            await self.page.wait_for_timeout(1000)
            
            modal_selectors = [
                'button:has-text("OK")',
                'button:has-text("Close")',
                '[role="dialog"] button'
            ]
            
            for selector in modal_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button and await button.is_visible():
                        await button.click()
                        print(f"✅ Dismissed modal with {selector}")
                        await self.page.wait_for_timeout(1000)
                        return True
                except:
                    continue
            
            return True
            
        except Exception as e:
            print(f"❌ Error dismissing modals: {e}")
            return False
    
    async def fill_initial_form_section(self, scenario: Dict) -> bool:
        """Fill the initial form section to reach dropdowns."""
        try:
            print("📋 Filling initial form section...")
            
            # Basic fields
            basic_fields = [
                ('input[name="firstname"]', 'Test'),
                ('input[name="surname"]', 'User'),
                ('input[name="email"]', f'test-{scenario["scenario_id"]}@example.com'),
                ('input[name="purchase"]', '1000000'),
                ('input[name="loan_amount"]', '100000')
            ]
            
            for selector, value in basic_fields:
                try:
                    field = await self.page.query_selector(selector)
                    if field and await field.is_visible():
                        await field.fill(value)
                        print(f"✅ Filled {selector}")
                except:
                    pass
            
            # Joint application checkbox
            if scenario['applicant_type'] == 'joint':
                joint_checkbox = await self.page.query_selector('input[type="checkbox"]')
                if joint_checkbox:
                    try:
                        await joint_checkbox.check()
                        print("✅ Checked joint application")
                        await self.page.wait_for_timeout(2000)
                    except:
                        pass
            
            # Submit to progress
            submit_button = await self.page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await self.page.wait_for_timeout(3000)
                
                # Handle modal
                await self.dismiss_modals()
                await self.page.wait_for_load_state("networkidle")
                
                print("✅ Progressed to Property and Mortgage section")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error filling initial section: {e}")
            return False
    
    async def complete_dropdowns_with_javascript(self) -> bool:
        """Complete dropdowns using direct JavaScript execution."""
        try:
            print("🎯 Completing dropdowns with JavaScript...")
            
            # Take screenshot before
            await self.page.screenshot(path="before_js_dropdown_fix.png")
            
            # JavaScript to find and set dropdowns
            js_code = """
            function completeDropdowns() {
                let results = {
                    reasonSet: false,
                    propertySet: false,
                    selects: []
                };
                
                // Find all select elements
                const selects = document.querySelectorAll('select');
                console.log('Found', selects.length, 'select elements');
                
                selects.forEach((select, index) => {
                    const name = select.name || '';
                    const id = select.id || '';
                    const options = Array.from(select.options).map(opt => opt.text);
                    
                    results.selects.push({
                        index: index,
                        name: name,
                        id: id,
                        options: options,
                        selectedIndex: select.selectedIndex,
                        selectedValue: select.value
                    });
                    
                    console.log(`Select ${index}: name="${name}", id="${id}", options=[${options.join(', ')}]`);
                    
                    // Try to identify and set reason for mortgage
                    if (name.toLowerCase().includes('reason') || 
                        select.closest('*')?.textContent?.toLowerCase().includes('reason for mortgage')) {
                        
                        console.log('Found reason dropdown at index', index);
                        
                        // Try to find purchase-related option
                        for (let i = 0; i < select.options.length; i++) {
                            const option = select.options[i];
                            const text = option.text.toLowerCase();
                            
                            if (text.includes('purchase') || text.includes('buy') || 
                                text.includes('home') || (i === 1 && text !== '')) {
                                select.selectedIndex = i;
                                select.value = option.value;
                                
                                // Trigger change events
                                select.dispatchEvent(new Event('change', { bubbles: true }));
                                select.dispatchEvent(new Event('input', { bubbles: true }));
                                
                                console.log('Set reason to:', option.text);
                                results.reasonSet = true;
                                break;
                            }
                        }
                    }
                    
                    // Try to identify and set property type
                    if (name.toLowerCase().includes('property') || name.toLowerCase().includes('type') ||
                        select.closest('*')?.textContent?.toLowerCase().includes('property type')) {
                        
                        console.log('Found property type dropdown at index', index);
                        
                        // Try to find house-related option
                        for (let i = 0; i < select.options.length; i++) {
                            const option = select.options[i];
                            const text = option.text.toLowerCase();
                            
                            if (text.includes('house') || text.includes('detached') || 
                                text.includes('home') || (i === 1 && text !== '')) {
                                select.selectedIndex = i;
                                select.value = option.value;
                                
                                // Trigger change events
                                select.dispatchEvent(new Event('change', { bubbles: true }));
                                select.dispatchEvent(new Event('input', { bubbles: true }));
                                
                                console.log('Set property type to:', option.text);
                                results.propertySet = true;
                                break;
                            }
                        }
                    }
                });
                
                // If we couldn't identify by name, try by position
                if (!results.reasonSet && selects.length > 0) {
                    const firstSelect = selects[0];
                    if (firstSelect.options.length > 1) {
                        firstSelect.selectedIndex = 1;
                        firstSelect.value = firstSelect.options[1].value;
                        firstSelect.dispatchEvent(new Event('change', { bubbles: true }));
                        console.log('Set first dropdown to first option:', firstSelect.options[1].text);
                        results.reasonSet = true;
                    }
                }
                
                if (!results.propertySet && selects.length > 1) {
                    const secondSelect = selects[1];
                    if (secondSelect.options.length > 1) {
                        secondSelect.selectedIndex = 1;
                        secondSelect.value = secondSelect.options[1].value;
                        secondSelect.dispatchEvent(new Event('change', { bubbles: true }));
                        console.log('Set second dropdown to first option:', secondSelect.options[1].text);
                        results.propertySet = true;
                    }
                }
                
                return results;
            }
            
            return completeDropdowns();
            """
            
            # Execute JavaScript
            js_result = await self.page.evaluate(js_code)
            print(f"JavaScript execution result: {js_result}")
            
            # Wait for changes to take effect
            await self.page.wait_for_timeout(2000)
            
            # Take screenshot after
            await self.page.screenshot(path="after_js_dropdown_fix.png")
            
            return js_result.get('reasonSet', False) or js_result.get('propertySet', False)
            
        except Exception as e:
            print(f"❌ Error with JavaScript dropdown fix: {e}")
            return False
    
    async def progress_to_income_section(self, scenario: Dict, max_attempts: int = 5) -> bool:
        """Progress through remaining sections until reaching income fields."""
        try:
            print("🚀 Progressing to income section...")
            
            for attempt in range(max_attempts):
                print(f"\\n--- ATTEMPT {attempt + 1}/{max_attempts} ---")
                
                # Complete any visible dropdowns
                await self.complete_dropdowns_with_javascript()
                
                # Set any visible radio buttons
                await self.set_common_radio_buttons()
                
                # Take screenshot before submit
                await self.page.screenshot(path=f"attempt_{attempt + 1}_before_submit.png")
                
                # Submit
                submit_button = await self.page.query_selector('button[type="submit"], input[type="submit"]')
                if not submit_button:
                    print("❌ No submit button found")
                    break
                
                await submit_button.click()
                await self.page.wait_for_timeout(3000)
                
                # Handle modals
                await self.dismiss_modals()
                await self.page.wait_for_load_state("networkidle")
                
                # Take screenshot after submit
                await self.page.screenshot(path=f"attempt_{attempt + 1}_after_submit.png")
                
                # Check if we've reached income section
                page_text = await self.page.text_content('body')
                
                # Look for income fields
                income_fields = await self.page.query_selector_all('input[name*="income"], input[name*="salary"], input[name*="net_profit"], input[name*="employment"]')
                visible_income = 0
                for field in income_fields:
                    try:
                        if await field.is_visible():
                            visible_income += 1
                    except:
                        pass
                
                print(f"Found {len(income_fields)} total income fields, {visible_income} visible")
                
                # Check for employment/applicant section indicators
                success_indicators = ['employment status', 'applicant details', 'income', 'salary']
                found_indicators = [ind for ind in success_indicators if ind in page_text.lower()]
                
                if visible_income > 0:
                    print(f"🎉 SUCCESS! Found {visible_income} visible income fields!")
                    return True
                elif found_indicators:
                    print(f"✅ Found section indicators: {found_indicators}")
                    # Continue to next attempt
                elif 'please' in page_text.lower() and ('choose' in page_text.lower() or 'select' in page_text.lower()):
                    print("⚠️ Still have validation errors, continuing...")
                else:
                    print("⚠️ Progressed but not sure where we are, continuing...")
                
                await self.page.wait_for_timeout(2000)
            
            print("⚠️ Completed maximum attempts without finding visible income fields")
            return False
            
        except Exception as e:
            print(f"❌ Error progressing to income section: {e}")
            return False
    
    async def set_common_radio_buttons(self) -> bool:
        """Set common radio button selections."""
        try:
            # Common selections
            radio_settings = [
                ('input[type="radio"][value="Yes"]', 'main residence'),
                ('input[type="radio"][value="No"]', 'debt consolidation'),
                ('input[type="radio"][value="No"]', 'green mortgage'), 
                ('input[type="radio"][value="Freehold"]', 'tenure'),
                ('input[type="radio"][value="No"]', 'later life')
            ]
            
            for selector, context in radio_settings:
                try:
                    radio = await self.page.query_selector(selector)
                    if radio and await radio.is_visible():
                        await radio.check()
                        print(f"✅ Set {context} radio")
                except:
                    pass
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting radio buttons: {e}")
            return False
    
    async def fill_income_fields(self, scenario: Dict) -> bool:
        """Fill income fields based on employment type."""
        try:
            print("💰 Filling income fields...")
            
            income_amount = scenario['applicant1_income']
            
            # First, set employment status if dropdowns are available
            await self.set_employment_status(scenario)
            
            # Look for income fields
            income_selectors = [
                'input[name*="income"]',
                'input[name*="salary"]', 
                'input[name*="basic"]',
                'input[name*="net_profit"]',
                'input[name*="employed"]'
            ]
            
            income_fields = []
            for selector in income_selectors:
                fields = await self.page.query_selector_all(selector)
                for field in fields:
                    try:
                        if await field.is_visible():
                            name = await field.get_attribute('name')
                            income_fields.append((field, name))
                    except:
                        pass
            
            print(f"Found {len(income_fields)} visible income fields")
            
            if len(income_fields) == 0:
                print("⚠️ No visible income fields found")
                return False
            
            filled_count = 0
            
            if scenario['applicant1_employment'] == 'employed':
                # Fill employed income fields
                for field, name in income_fields:
                    try:
                        await field.fill(str(income_amount))
                        print(f"✅ Filled {name} with £{income_amount:,}")
                        filled_count += 1
                    except Exception as e:
                        print(f"⚠️ Could not fill {name}: {e}")
            
            else:
                # Fill self-employed income fields
                year1_amount = income_amount
                year2_amount = income_amount // 2
                year3_amount = 0
                
                for field, name in income_fields:
                    try:
                        if 'year_1' in name.lower() or 'last' in name.lower() or 'current' in name.lower():
                            await field.fill(str(year1_amount))
                            print(f"✅ Filled {name} (Year 1) with £{year1_amount:,}")
                            filled_count += 1
                        elif 'year_2' in name.lower():
                            await field.fill(str(year2_amount))
                            print(f"✅ Filled {name} (Year 2) with £{year2_amount:,}")
                            filled_count += 1
                        elif 'year_3' in name.lower():
                            await field.fill(str(year3_amount))
                            print(f"✅ Filled {name} (Year 3) with £{year3_amount:,}")
                            filled_count += 1
                        else:
                            await field.fill(str(year1_amount))
                            print(f"✅ Filled {name} with £{year1_amount:,}")
                            filled_count += 1
                    except Exception as e:
                        print(f"⚠️ Could not fill {name}: {e}")
                
                # Set time in business
                await self.set_time_in_business()
            
            print(f"📊 Successfully filled {filled_count} income fields")
            return filled_count > 0
            
        except Exception as e:
            print(f"❌ Error filling income fields: {e}")
            return False
    
    async def set_employment_status(self, scenario: Dict) -> bool:
        """Set employment status dropdowns."""
        try:
            employment_value = 'Employed' if scenario['applicant1_employment'] == 'employed' else 'Self Employed'
            
            # Look for employment dropdowns
            employment_selectors = [
                'select[name*="employment"]',
                'select[name*="status"]'
            ]
            
            for selector in employment_selectors:
                try:
                    select = await self.page.query_selector(selector)
                    if select and await select.is_visible():
                        await select.select_option(employment_value)
                        print(f"✅ Set employment status to: {employment_value}")
                        await self.page.wait_for_timeout(2000)  # Wait for fields to appear
                        return True
                except:
                    continue
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting employment status: {e}")
            return False
    
    async def set_time_in_business(self) -> bool:
        """Set time in business for self-employed."""
        try:
            print("📅 Setting time in business: 2 years 0 months")
            
            # Look for business time dropdowns
            selects = await self.page.query_selector_all('select')
            
            for select in selects:
                try:
                    name = await select.get_attribute('name') or ''
                    if 'business' in name.lower():
                        if 'year' in name.lower():
                            await select.select_option('2')
                            print("✅ Set business years: 2")
                        elif 'month' in name.lower():
                            await select.select_option('0')
                            print("✅ Set business months: 0")
                except:
                    pass
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting time in business: {e}")
            return False
    
    async def submit_and_extract_results(self, scenario: Dict) -> Dict[str, float]:
        """Submit final form and extract results."""
        try:
            print("🚀 Final submission and results extraction...")
            
            # Take screenshot before final submit
            await self.page.screenshot(path=f"before_final_submit_{scenario['scenario_id']}.png")
            
            # Submit
            submit_button = await self.page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                print("📤 Final form submitted")
                
                # Wait for results
                await self.page.wait_for_timeout(15000)
                await self.page.wait_for_load_state("networkidle", timeout=60000)
                
                # Take screenshot of results
                await self.page.screenshot(path=f"final_results_{scenario['scenario_id']}.png")
                print("📸 Results screenshot saved")
                
                # Extract results
                results = await self.extract_lender_results()
                return results
            else:
                print("❌ No final submit button found")
                return {}
                
        except Exception as e:
            print(f"❌ Error in final submission: {e}")
            return {}
    
    async def extract_lender_results(self) -> Dict[str, float]:
        """Extract lender results from the results page."""
        try:
            print("📊 Extracting lender results...")
            results = {}
            
            # Get page content
            page_text = await self.page.text_content('body')
            
            # Also try to find results in tables
            tables = await self.page.query_selector_all('table')
            print(f"Found {len(tables)} tables on results page")
            
            # Try table extraction first
            for table in tables:
                try:
                    table_text = await table.text_content()
                    lender_count = sum(1 for lender in self.target_lenders if lender.lower() in table_text.lower())
                    
                    if lender_count >= 3:  # Likely a results table
                        print(f"Found results table with {lender_count} lenders")
                        
                        rows = await table.query_selector_all('tr')
                        for row in rows:
                            row_text = await row.text_content()
                            
                            for lender in self.target_lenders:
                                if lender.lower() in row_text.lower():
                                    # Extract amounts from this row
                                    amounts = re.findall(r'£([\\d,]+)', row_text)
                                    if amounts:
                                        try:
                                            max_amount = max(float(amt.replace(',', '')) for amt in amounts)
                                            if max_amount > 1000:
                                                results[lender] = max_amount
                                                print(f"✅ {lender}: £{max_amount:,.0f}")
                                        except:
                                            pass
                        break
                except:
                    continue
            
            # If no table results, try text extraction
            if not results:
                print("No table results found, trying text extraction...")
                
                for lender in self.target_lenders:
                    patterns = [
                        rf'{re.escape(lender)}.*?£([\\d,]+)',
                        rf'{lender}.*?£([\\d,]+)',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, page_text, re.IGNORECASE | re.DOTALL)
                        if matches:
                            amounts = []
                            for match in matches:
                                try:
                                    amount = float(str(match).replace(',', ''))
                                    if amount > 1000:
                                        amounts.append(amount)
                                except:
                                    continue
                            
                            if amounts:
                                max_amount = max(amounts)
                                results[lender] = max_amount
                                print(f"✅ {lender}: £{max_amount:,.0f}")
                                break
            
            print(f"📈 Extracted {len(results)} lender results")
            return results
            
        except Exception as e:
            print(f"❌ Error extracting results: {e}")
            return {}
    
    async def run_complete_scenario(self, scenario: Dict) -> Dict[str, float]:
        """Run complete end-to-end scenario."""
        try:
            print(f"\\n🎯 === RUNNING COMPLETE SCENARIO: {scenario['scenario_id']} ===")
            print(f"Type: {scenario['applicant_type']}")
            print(f"Income: £{scenario['applicant1_income']:,}")
            print(f"Employment: {scenario['applicant1_employment']}")
            
            # Step 1: Create case
            if not await self.create_new_case(scenario):
                return {}
            
            # Step 2: Fill initial form and reach dropdowns
            if not await self.fill_initial_form_section(scenario):
                return {}
            
            # Step 3: Progress through sections to income fields
            if not await self.progress_to_income_section(scenario):
                print("⚠️ Could not reach income section, but continuing...")
            
            # Step 4: Fill income fields
            if not await self.fill_income_fields(scenario):
                print("⚠️ Could not fill income fields, but continuing...")
            
            # Step 5: Submit and extract results
            results = await self.submit_and_extract_results(scenario)
            
            return results
            
        except Exception as e:
            print(f"❌ Error running complete scenario: {e}")
            return {}
    
    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()


# Test function
async def test_end_to_end():
    """Test the complete end-to-end automation."""
    mbt = MBTEndToEndAutomation()
    
    try:
        await mbt.start_browser(headless=False)
        
        if not await mbt.login():
            print("Login failed")
            return
        
        # Test with employed scenario
        test_scenario = {
            'scenario_id': 'end_to_end_employed_test',
            'scenario_type': 'vanilla',
            'applicant_type': 'joint',
            'applicant1_income': 40000,
            'applicant2_income': 40000,
            'applicant1_employment': 'employed',
            'applicant2_employment': 'employed',
            'age': 30,
            'term': 35
        }
        
        results = await mbt.run_complete_scenario(test_scenario)
        
        if results:
            print(f"\\n🎉 SUCCESS! End-to-end results for {test_scenario['scenario_id']}:")
            for lender, amount in results.items():
                print(f"   {lender}: £{amount:,.0f}")
            
            print(f"\\n📊 SUMMARY:")
            print(f"   Total lenders: {len(results)}")
            if results:
                avg_amount = sum(results.values()) / len(results)
                max_amount = max(results.values())
                min_amount = min(results.values())
                print(f"   Average: £{avg_amount:,.0f}")
                print(f"   Max: £{max_amount:,.0f}")
                print(f"   Min: £{min_amount:,.0f}")
        else:
            print(f"\\n❌ No results obtained for {test_scenario['scenario_id']}")
    
    finally:
        print("\\n⏳ Keeping browser open for inspection...")
        await asyncio.sleep(60)
        await mbt.close()


if __name__ == "__main__":
    asyncio.run(test_end_to_end())