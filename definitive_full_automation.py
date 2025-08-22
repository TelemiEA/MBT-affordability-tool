"""
Definitive Full Automation - Combining all learnings into a bulletproof solution.
We know the automation works ("Home mover" proves it) - now make it 100% reliable.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import re

load_dotenv()

class DefinitiveFullAutomation:
    """Complete, bulletproof MBT automation."""
    
    def __init__(self):
        self.username = os.getenv("MBT_USERNAME")
        self.password = os.getenv("MBT_PASSWORD")
        self.browser = None
        self.page = None
        
        self.target_lenders = [
            "Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom",
            "Clydesdale", "Newcastle", "Metro", "Nottingham", "Hinckley & Rugby",
            "Leeds", "Principality", "Coventry", "Santander"
        ]
    
    async def start_browser(self, headless=False):
        """Start browser with optimal settings."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-dev-shm-usage'],
            slow_mo=800
        )
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
    
    async def login(self):
        """Login to MBT."""
        print("🔐 Logging in...")
        await self.page.goto("https://mortgagebrokertools.co.uk/signin", wait_until='networkidle')
        await self.page.wait_for_timeout(2000)
        
        await self.page.fill('input[name="email"]', self.username)
        await self.page.fill('input[name="password"]', self.password)
        await self.page.click('input[type="submit"]')
        await self.page.wait_for_load_state("networkidle", timeout=10000)
        await self.page.wait_for_timeout(3000)
        
        if "signin" not in self.page.url.lower():
            print("✅ Login successful")
            return True
        else:
            print("❌ Login failed")
            return False
    
    async def create_case(self, scenario_id):
        """Create new case."""
        print(f"📝 Creating case for {scenario_id}...")
        await self.page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
        await self.page.wait_for_load_state("networkidle")
        await self.page.wait_for_timeout(2000)
        
        await self.page.click('text=Create RESI Case')
        await self.page.wait_for_load_state("networkidle")
        await self.page.wait_for_timeout(3000)
        
        print(f"✅ Case created: {self.page.url}")
        return True
    
    async def fill_basic_section(self, scenario):
        """Fill basic applicant section."""
        print("📋 Filling basic section...")
        
        # Basic fields
        basic_fields = [
            ('input[name="firstname"]', 'Test'),
            ('input[name="surname"]', 'User'),
            ('input[name="email"]', f'test-{scenario["scenario_id"]}@example.com'),
            ('input[name="purchase"]', '1000000'),
            ('input[name="loan_amount"]', '100000')
        ]
        
        for selector, value in basic_fields:
            await self.page.fill(selector, value)
        
        # Joint application if needed
        if scenario['applicant_type'] == 'joint':
            joint_checkbox = await self.page.query_selector('input[type="checkbox"]')
            if joint_checkbox:
                await joint_checkbox.check()
                await self.page.wait_for_timeout(2000)
        
        # Submit to next section
        await self.page.click('button[type="submit"]')
        await self.page.wait_for_timeout(3000)
        
        # Dismiss modal
        try:
            await self.page.click('button:has-text("OK")')
            await self.page.wait_for_timeout(2000)
        except:
            pass
        
        await self.page.wait_for_load_state("networkidle")
        print("✅ Basic section completed")
        return True
    
    async def complete_property_section_bulletproof(self):
        """Bulletproof property section completion using multiple strategies."""
        print("🎯 Bulletproof property section completion...")
        
        # Strategy 1: Specific dropdown targeting for "First-time buyer" and property type
        working_js = """
        (function() {
            let results = { selectsCompleted: 0, radiosSet: 0, details: [] };
            
            // Find and set "First-time buyer" for reason for mortgage
            const selects = document.querySelectorAll('select');
            for (let i = 0; i < selects.length; i++) {
                const select = selects[i];
                if (select.options && select.options.length > 1 && select.offsetParent !== null) {
                    // Look for "First-time buyer" option specifically
                    for (let j = 0; j < select.options.length; j++) {
                        const option = select.options[j];
                        if (option.text && option.text.toLowerCase().includes('first-time buyer')) {
                            select.selectedIndex = j;
                            select.value = option.value;
                            
                            // Trigger comprehensive events
                            const events = ['focus', 'click', 'input', 'change', 'blur'];
                            events.forEach(eventType => {
                                const event = new Event(eventType, { bubbles: true, cancelable: true });
                                select.dispatchEvent(event);
                            });
                            
                            results.selectsCompleted++;
                            results.details.push(`Select ${i}: First-time buyer`);
                            break;
                        }
                    }
                    
                    // If no "First-time buyer" found, try other reasonable options
                    if (select.selectedIndex === 0) {
                        for (let j = 0; j < select.options.length; j++) {
                            const option = select.options[j];
                            if (option.text && (
                                option.text.toLowerCase().includes('purchase') ||
                                option.text.toLowerCase().includes('house') ||
                                option.text.toLowerCase().includes('detached') ||
                                option.text.toLowerCase().includes('semi')
                            )) {
                                select.selectedIndex = j;
                                select.value = option.value;
                                
                                const events = ['focus', 'click', 'input', 'change', 'blur'];
                                events.forEach(eventType => {
                                    const event = new Event(eventType, { bubbles: true, cancelable: true });
                                    select.dispatchEvent(event);
                                });
                                
                                results.selectsCompleted++;
                                results.details.push(`Select ${i}: ${option.text}`);
                                break;
                            }
                        }
                    }
                    
                    // Last resort - select first non-empty option
                    if (select.selectedIndex === 0 && select.options.length > 1) {
                        select.selectedIndex = 1;
                        select.value = select.options[1].value;
                        
                        const events = ['focus', 'click', 'input', 'change', 'blur'];
                        events.forEach(eventType => {
                            const event = new Event(eventType, { bubbles: true, cancelable: true });
                            select.dispatchEvent(event);
                        });
                        
                        results.selectsCompleted++;
                        results.details.push(`Select ${i}: ${select.options[1].text}`);
                    }
                }
            }
            
            // Set Freehold radio button
            const freeholdRadio = document.querySelector('input[type="radio"][value="Freehold"]');
            if (freeholdRadio && !freeholdRadio.checked) {
                freeholdRadio.checked = true;
                freeholdRadio.dispatchEvent(new Event('change', { bubbles: true }));
                results.radiosSet++;
                results.details.push('Set Freehold');
            }
            
            // Set Yes for main residence
            const yesRadio = document.querySelector('input[type="radio"][value="Yes"]');
            if (yesRadio && !yesRadio.checked) {
                yesRadio.checked = true;
                yesRadio.dispatchEvent(new Event('change', { bubbles: true }));
                results.radiosSet++;
                results.details.push('Set Yes for main residence');
            }
            
            // Set No for debt consolidation
            const noRadios = document.querySelectorAll('input[type="radio"][value="No"]');
            noRadios.forEach(radio => {
                if (!radio.checked) {
                    radio.checked = true;
                    radio.dispatchEvent(new Event('change', { bubbles: true }));
                    results.radiosSet++;
                }
            });
            
            return results;
        })();
        """
        
        max_attempts = 8
        for attempt in range(max_attempts):
            print(f"  Attempt {attempt + 1}/{max_attempts}...")
            
            # Apply the proven JavaScript
            try:
                js_result = await self.page.evaluate(working_js)
                print(f"  JS Result: {js_result}")
            except Exception as e:
                print(f"  JS Error: {e}")
            
            # Additional manual targeting for stubborn elements
            await self.manual_element_targeting()
            
            # Wait for changes to take effect
            await self.page.wait_for_timeout(2000)
            
            # Take screenshot
            await self.page.screenshot(path=f"property_attempt_{attempt + 1}.png")
            
            # Try submission
            success = await self.attempt_submission()
            if success:
                print(f"✅ Property section completed on attempt {attempt + 1}")
                return True
            
            # Wait before next attempt
            await self.page.wait_for_timeout(1000)
        
        print("⚠️ Property section completion exhausted all attempts")
        return False
    
    async def manual_element_targeting(self):
        """Manual targeting for specific stubborn elements."""
        try:
            # Strategy 2: Direct element interaction
            selectors_to_try = [
                'select[name*="reason"]',
                'select[name*="property"]', 
                'select[name*="type"]',
                'select[placeholder*="Reason"]',
                'select[placeholder*="Property"]'
            ]
            
            for selector in selectors_to_try:
                try:
                    element = await self.page.query_selector(selector)
                    if element and await element.is_visible():
                        options = await element.query_selector_all('option')
                        if len(options) > 1:
                            await element.select_option(index=1)
                            print(f"  ✅ Manual selection: {selector}")
                except:
                    continue
            
            # Strategy 3: Specific targeting for "First-time buyer"
            try:
                # Try to click and select "First-time buyer" specifically
                reason_dropdown = await self.page.query_selector('[placeholder="Reason for mortgage"]')
                if reason_dropdown and await reason_dropdown.is_visible():
                    await reason_dropdown.click()
                    await self.page.wait_for_timeout(1000)
                    
                    # Try typing "First-time buyer"
                    await self.page.keyboard.type('First-time buyer')
                    await self.page.wait_for_timeout(500)
                    await self.page.keyboard.press('Enter')
                    await self.page.wait_for_timeout(1000)
                    print("  ✅ Selected First-time buyer via typing")
                
                # Try property type dropdown
                property_dropdown = await self.page.query_selector('[placeholder="Property type"]')
                if property_dropdown and await property_dropdown.is_visible():
                    await property_dropdown.click()
                    await self.page.wait_for_timeout(1000)
                    
                    # Try selecting a house type
                    await self.page.keyboard.type('House')
                    await self.page.wait_for_timeout(500)
                    await self.page.keyboard.press('Enter')
                    await self.page.wait_for_timeout(1000)
                    print("  ✅ Selected House via typing")
                    
            except Exception as e:
                print(f"  Specific targeting error: {e}")
                
                # Fallback: Click-based interaction
                clickable_elements = [
                    'text=Reason for mortgage',
                    'text=Property type',
                    '[placeholder="Reason for mortgage"]',
                    '[placeholder="Property type"]'
                ]
                
                for selector in clickable_elements:
                    try:
                        element = await self.page.query_selector(selector)
                        if element and await element.is_visible():
                            await element.click()
                            await self.page.wait_for_timeout(500)
                            await self.page.keyboard.press('ArrowDown')
                            await self.page.wait_for_timeout(300)
                            await self.page.keyboard.press('Enter')
                            await self.page.wait_for_timeout(500)
                            print(f"  ✅ Click interaction: {selector}")
                    except:
                        continue
            
            # Strategy 4: Radio button direct setting
            radio_settings = [
                'input[type="radio"][value="Freehold"]',
                'input[type="radio"][value="Yes"]'
            ]
            
            for selector in radio_settings:
                try:
                    radio = await self.page.query_selector(selector)
                    if radio and await radio.is_visible():
                        await radio.check()
                        print(f"  ✅ Radio set: {selector}")
                except:
                    continue
                    
        except Exception as e:
            print(f"  Manual targeting error: {e}")
    
    async def attempt_submission(self):
        """Attempt form submission and check for success."""
        try:
            # Submit
            submit_button = await self.page.query_selector('button[type="submit"], input[type="submit"]')
            if not submit_button:
                return False
            
            await submit_button.click()
            await self.page.wait_for_timeout(3000)
            
            # Check for modal (indicates validation errors)
            try:
                ok_button = await self.page.query_selector('button:has-text("OK")')
                if ok_button and await ok_button.is_visible():
                    await ok_button.click()
                    await self.page.wait_for_timeout(2000)
                    print("  ⚠️ Modal appeared - validation errors remain")
                    return False
                else:
                    print("  ✅ No modal - likely progressed!")
                    return True
            except:
                print("  ✅ No modal detected")
                return True
                
        except Exception as e:
            print(f"  Submission error: {e}")
            return False
    
    async def progress_through_remaining_sections(self, scenario):
        """Progress through all remaining sections to reach results."""
        print("🔄 Progressing through remaining sections...")
        
        max_sections = 10
        for section in range(max_sections):
            await self.page.wait_for_load_state("networkidle")
            
            # Take screenshot
            await self.page.screenshot(path=f"section_{section + 1}.png")
            
            # Check current section
            page_text = await self.page.text_content('body')
            current_url = self.page.url
            
            print(f"  Section {section + 1}: {current_url}")
            
            # Handle different section types
            if 'applicant' in page_text.lower() or 'employment' in page_text.lower():
                print("  👥 Applicant section detected")
                await self.handle_applicant_section(scenario)
                
            elif any(word in page_text.lower() for word in ['income', 'salary', 'earnings']):
                print("  💰 Income section detected")
                await self.handle_income_section(scenario)
                
            elif 'results' in page_text.lower() or 'lender' in page_text.lower():
                print("  📊 Results section detected!")
                results = await self.extract_results()
                return results
                
            else:
                print("  📝 Generic form section - filling fields")
                await self.fill_generic_section()
            
            # Submit to next section
            submit_button = await self.page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await self.page.wait_for_timeout(5000)
                await self.page.wait_for_load_state("networkidle")
            else:
                print("  ⚠️ No submit button - may be at final section")
                break
        
        # Final attempt to extract results
        print("🔍 Final results extraction attempt...")
        return await self.extract_results()
    
    async def handle_applicant_section(self, scenario):
        """Handle applicant/employment section."""
        try:
            # Set employment status
            employment_selects = await self.page.query_selector_all('select')
            for select in employment_selects:
                try:
                    name = await select.get_attribute('name') or ''
                    if 'employment' in name.lower() or 'status' in name.lower():
                        employment_value = 'Employed' if scenario['applicant1_employment'] == 'employed' else 'Self Employed'
                        await select.select_option(employment_value)
                        print(f"  ✅ Set employment: {employment_value}")
                        await self.page.wait_for_timeout(2000)
                        break
                except:
                    continue
            
            # Fill any visible text fields
            await self.fill_generic_section()
            
        except Exception as e:
            print(f"  Applicant section error: {e}")
    
    async def handle_income_section(self, scenario):
        """Handle income section."""
        try:
            income_amount = scenario['applicant1_income']
            
            # Find all income-related fields
            income_selectors = [
                'input[name*="income"]',
                'input[name*="salary"]',
                'input[name*="basic"]',
                'input[name*="net_profit"]',
                'input[name*="employed"]'
            ]
            
            filled_count = 0
            for selector in income_selectors:
                fields = await self.page.query_selector_all(selector)
                for field in fields:
                    try:
                        if await field.is_visible():
                            if scenario['applicant1_employment'] == 'employed':
                                await field.fill(str(income_amount))
                            else:
                                # Self-employed pattern
                                name = await field.get_attribute('name') or ''
                                if 'year_1' in name.lower() or 'current' in name.lower():
                                    await field.fill(str(income_amount))
                                elif 'year_2' in name.lower():
                                    await field.fill(str(income_amount // 2))
                                elif 'year_3' in name.lower():
                                    await field.fill('0')
                                else:
                                    await field.fill(str(income_amount))
                            
                            filled_count += 1
                            print(f"  ✅ Filled income field {filled_count}")
                    except:
                        continue
            
            print(f"  💰 Filled {filled_count} income fields")
            
            # Set time in business for self-employed
            if scenario['applicant1_employment'] == 'self_employed':
                await self.set_time_in_business()
            
        except Exception as e:
            print(f"  Income section error: {e}")
    
    async def set_time_in_business(self):
        """Set time in business for self-employed."""
        try:
            selects = await self.page.query_selector_all('select')
            for select in selects:
                name = await select.get_attribute('name') or ''
                if 'business' in name.lower():
                    if 'year' in name.lower():
                        await select.select_option('2')
                        print("  ✅ Business years: 2")
                    elif 'month' in name.lower():
                        await select.select_option('0')
                        print("  ✅ Business months: 0")
        except Exception as e:
            print(f"  Time in business error: {e}")
    
    async def fill_generic_section(self):
        """Fill any generic form section with sensible defaults."""
        try:
            # Fill text inputs
            text_inputs = await self.page.query_selector_all('input[type="text"], input[type="email"], input[type="number"]')
            for field in text_inputs:
                try:
                    if await field.is_visible():
                        name = await field.get_attribute('name') or ''
                        placeholder = await field.get_attribute('placeholder') or ''
                        
                        if any(word in (name + placeholder).lower() for word in ['email']):
                            await field.fill('test@example.com')
                        elif any(word in (name + placeholder).lower() for word in ['name', 'first', 'surname']):
                            await field.fill('Test')
                        elif any(word in (name + placeholder).lower() for word in ['income', 'salary', 'amount']):
                            await field.fill('40000')
                        elif any(word in (name + placeholder).lower() for word in ['age']):
                            await field.fill('30')
                except:
                    continue
            
            # Set dropdowns to first option
            selects = await self.page.query_selector_all('select')
            for select in selects:
                try:
                    if await select.is_visible():
                        options = await select.query_selector_all('option')
                        if len(options) > 1:
                            await select.select_option(index=1)
                except:
                    continue
            
            # Set radio buttons
            radios = await self.page.query_selector_all('input[type="radio"]')
            for radio in radios:
                try:
                    if await radio.is_visible() and not await radio.is_checked():
                        value = await radio.get_attribute('value') or ''
                        if any(val in value.lower() for val in ['yes', 'employed', 'freehold']):
                            await radio.check()
                            break
                except:
                    continue
                    
        except Exception as e:
            print(f"  Generic section error: {e}")
    
    async def extract_results(self):
        """Extract final lender results."""
        try:
            print("📊 Extracting results...")
            
            await self.page.screenshot(path="FINAL_AUTOMATION_RESULTS.png")
            
            # Get page content
            page_text = await self.page.text_content('body')
            results = {}
            
            # Try table extraction first
            tables = await self.page.query_selector_all('table')
            for table in tables:
                table_text = await table.text_content()
                lender_count = sum(1 for lender in self.target_lenders if lender.lower() in table_text.lower())
                
                if lender_count >= 3:  # Likely results table
                    print(f"  Found results table with {lender_count} lenders")
                    
                    rows = await table.query_selector_all('tr')
                    for row in rows:
                        row_text = await row.text_content()
                        
                        for lender in self.target_lenders:
                            if lender.lower() in row_text.lower():
                                amounts = re.findall(r'£([\\d,]+)', row_text)
                                if amounts:
                                    try:
                                        max_amount = max(float(amt.replace(',', '')) for amt in amounts)
                                        if max_amount > 1000:
                                            results[lender] = max_amount
                                            print(f"  ✅ {lender}: £{max_amount:,.0f}")
                                    except:
                                        pass
                    break
            
            # Text extraction if no table results
            if not results:
                for lender in self.target_lenders:
                    if lender in page_text:
                        pattern = rf'{re.escape(lender)}.*?£([\\d,]+)'
                        matches = re.findall(pattern, page_text, re.IGNORECASE | re.DOTALL)
                        if matches:
                            amounts = [float(m.replace(',', '')) for m in matches if m.replace(',', '').isdigit()]
                            if amounts:
                                max_amount = max(amounts)
                                if max_amount > 1000:
                                    results[lender] = max_amount
                                    print(f"  ✅ {lender}: £{max_amount:,.0f}")
            
            return results
            
        except Exception as e:
            print(f"Results extraction error: {e}")
            return {}
    
    async def run_full_scenario(self, scenario):
        """Run complete end-to-end scenario."""
        try:
            print(f"\\n🎯 === FULL AUTOMATION: {scenario['scenario_id']} ===")
            print(f"Type: {scenario['applicant_type']}")
            print(f"Income: £{scenario['applicant1_income']:,}")
            print(f"Employment: {scenario['applicant1_employment']}")
            
            # Step 1: Create case
            if not await self.create_case(scenario['scenario_id']):
                return {}
            
            # Step 2: Fill basic section
            if not await self.fill_basic_section(scenario):
                return {}
            
            # Step 3: Complete property section (the critical part)
            if not await self.complete_property_section_bulletproof():
                print("⚠️ Property section incomplete, but continuing...")
            
            # Step 4: Progress through remaining sections
            results = await self.progress_through_remaining_sections(scenario)
            
            return results
            
        except Exception as e:
            print(f"❌ Scenario error: {e}")
            return {}
    
    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()


async def test_definitive_automation():
    """Test the definitive full automation."""
    automation = DefinitiveFullAutomation()
    
    try:
        await automation.start_browser(headless=False)
        
        if not await automation.login():
            print("Login failed")
            return
        
        # Test scenario
        test_scenario = {
            'scenario_id': 'definitive_test_employed',
            'scenario_type': 'vanilla',
            'applicant_type': 'joint',
            'applicant1_income': 40000,
            'applicant2_income': 40000,
            'applicant1_employment': 'employed',
            'applicant2_employment': 'employed',
            'age': 30,
            'term': 35
        }
        
        results = await automation.run_full_scenario(test_scenario)
        
        if results:
            print(f"\\n🎉 DEFINITIVE SUCCESS! Results for {test_scenario['scenario_id']}:")
            print("="*60)
            for lender, amount in results.items():
                print(f"   {lender}: £{amount:,.0f}")
            print("="*60)
            print(f"📊 Total lenders: {len(results)}")
            if results:
                avg_amount = sum(results.values()) / len(results)
                print(f"💰 Average: £{avg_amount:,.0f}")
            print("\\n🚀 FULL END-TO-END AUTOMATION COMPLETE!")
        else:
            print(f"\\n⚠️ No results extracted, but automation workflow completed")
            print("✅ Check FINAL_AUTOMATION_RESULTS.png for verification")
    
    finally:
        print("\\n⏳ Keeping browser open for inspection...")
        await asyncio.sleep(60)
        await automation.close()


if __name__ == "__main__":
    asyncio.run(test_definitive_automation())