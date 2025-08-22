"""
Final MBT automation following the correct step-by-step workflow.
Focus on required fields (red asterisks) and proper field unlocking sequence.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv
import re

load_dotenv()

class MBTAutomationFinalV2:
    """Final MBT automation with correct workflow and field targeting."""
    
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
        
        # Default values as specified
        self.default_property_value = 1000000
        self.default_loan_amount = 100000
        self.default_term = 35
    
    async def start_browser(self, headless: bool = True):
        """Start browser with optimal settings."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-dev-shm-usage'],
            slow_mo=1000 if not headless else 0  # Slow down when visible
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
        """Create a new RESI case - fresh case for each scenario."""
        try:
            print(f"📝 Creating NEW case for {scenario['scenario_id']}...")
            
            # Always return to dashboard for clean state
            await self.page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await self.page.wait_for_load_state("networkidle")
            await self.page.wait_for_timeout(2000)
            
            # Create new RESI case
            await self.page.click('text=Create RESI Case')
            await self.page.wait_for_load_state("networkidle")
            await self.page.wait_for_timeout(3000)
            
            print(f"✅ New case created: {self.page.url}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating case: {e}")
            return False
    
    async def fill_required_basic_details(self, scenario: Dict) -> bool:
        """Fill required basic applicant details (red asterisk fields)."""
        try:
            print("👤 Filling required basic details...")
            
            # Focus only on required fields with red asterisks
            required_fields = [
                ('input[name="firstname"]', 'Test'),
                ('input[name="surname"]', 'User'),
                ('input[name="email"]', f'test-{scenario["scenario_id"]}@example.com')
            ]
            
            for selector, value in required_fields:
                try:
                    field = await self.page.query_selector(selector)
                    if field:
                        await field.fill(value)
                        print(f"✅ Filled {selector}")
                    else:
                        print(f"⚠️ Field not found: {selector}")
                except Exception as e:
                    print(f"❌ Error filling {selector}: {e}")
            
            print("✅ Basic details completed")
            return True
            
        except Exception as e:
            print(f"❌ Error in basic details: {e}")
            return False
    
    async def set_property_and_loan_defaults(self) -> bool:
        """Set default property value and loan amount."""
        try:
            print("🏡 Setting property and loan defaults...")
            
            # Property value - £1,000,000
            purchase_field = await self.page.query_selector('input[name="purchase"]')
            if purchase_field:
                await purchase_field.fill(str(self.default_property_value))
                print(f"✅ Property value set to £{self.default_property_value:,}")
            
            # Loan amount - £100,000
            loan_field = await self.page.query_selector('input[name="loan_amount"]')
            if loan_field:
                await loan_field.fill(str(self.default_loan_amount))
                print(f"✅ Loan amount set to £{self.default_loan_amount:,}")
            
            # Mortgage term - 35 years (dropdown)
            term_select = await self.page.query_selector('select[name*="term"]')
            if term_select:
                try:
                    await term_select.select_option(str(self.default_term))
                    print(f"✅ Term set to {self.default_term} years")
                except:
                    print("⚠️ Could not set term dropdown")
            
            print("✅ Property and loan defaults set")
            return True
            
        except Exception as e:
            print(f"❌ Error setting defaults: {e}")
            return False
    
    async def set_number_of_applicants(self, scenario: Dict) -> bool:
        """Set number of applicants - this unlocks employment sections."""
        try:
            applicant_count = 2 if scenario['applicant_type'] == 'joint' else 1
            print(f"👥 Setting number of applicants to {applicant_count}")
            
            # Look for applicant number dropdown
            applicant_selectors = [
                'select[name*="applicant"]',
                'select[name*="number"]',
                'select[id*="applicant"]'
            ]
            
            for selector in applicant_selectors:
                try:
                    applicant_select = await self.page.query_selector(selector)
                    if applicant_select:
                        await applicant_select.select_option(str(applicant_count))
                        print(f"✅ Set {applicant_count} applicant(s)")
                        
                        # Wait for form to update and show employment sections
                        await self.page.wait_for_timeout(2000)
                        return True
                except:
                    continue
            
            print("⚠️ Could not find applicant number dropdown")
            return True  # Continue anyway
            
        except Exception as e:
            print(f"❌ Error setting applicants: {e}")
            return False
    
    async def set_employment_status_and_unlock_income(self, scenario: Dict) -> bool:
        """Set employment status to unlock income fields."""
        try:
            print("👔 Setting employment status to unlock income fields...")
            
            # Determine employment status
            if scenario['applicant1_employment'] == 'employed':
                employment_value = 'Employed'
                print("Setting to: Employed")
            else:
                employment_value = 'Self Employed (Sole Trader)'
                print("Setting to: Self Employed (Sole Trader)")
            
            # Look for employment status dropdown
            employment_selectors = [
                'select[name*="employment"]',
                'select[name*="status"]',
                'select[id*="employment"]'
            ]
            
            employment_set = False
            for selector in employment_selectors:
                try:
                    employment_select = await self.page.query_selector(selector)
                    if employment_select and await employment_select.is_visible():
                        # Get all options to see what's available
                        options = await employment_select.query_selector_all('option')
                        option_texts = []
                        for option in options:
                            text = await option.text_content()
                            value = await option.get_attribute('value')
                            option_texts.append(f"'{text}' (value: {value})")
                        
                        print(f"Available options: {option_texts}")
                        
                        # Try to select the employment status
                        try:
                            await employment_select.select_option(employment_value)
                            print(f"✅ Set employment to: {employment_value}")
                            employment_set = True
                            break
                        except:
                            # Try alternative values
                            if 'employed' in employment_value.lower():
                                await employment_select.select_option('Employed')
                            else:
                                await employment_select.select_option('Self Employed')
                            print(f"✅ Set employment (alternative)")
                            employment_set = True
                            break
                            
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
            
            if employment_set:
                # CRITICAL: Wait for income fields to become visible
                print("⏳ Waiting for income fields to appear...")
                await self.page.wait_for_timeout(3000)
                
                # Verify income fields are now visible
                await self.verify_income_fields_visible(scenario)
                return True
            else:
                print("❌ Could not set employment status")
                return False
            
        except Exception as e:
            print(f"❌ Error setting employment: {e}")
            return False
    
    async def verify_income_fields_visible(self, scenario: Dict) -> bool:
        """Verify that income fields are now visible after setting employment."""
        try:
            print("🔍 Verifying income fields are visible...")
            
            if scenario['applicant1_employment'] == 'employed':
                # Look for employed income fields
                income_selectors = [
                    'input[name*="income_amount"]',
                    'input[name*="basic_salary"]',
                    'input[name*="salary"]'
                ]
            else:
                # Look for self-employed "net profit" fields
                income_selectors = [
                    'input[name*="net_profit"]',
                    'input[name*="self_employed_income"]'
                ]
            
            visible_fields = []
            for selector in income_selectors:
                fields = await self.page.query_selector_all(selector)
                for field in fields:
                    if await field.is_visible():
                        name = await field.get_attribute('name')
                        visible_fields.append(name)
            
            if visible_fields:
                print(f"✅ Found {len(visible_fields)} visible income fields:")
                for field in visible_fields:
                    print(f"   - {field}")
                return True
            else:
                print("❌ No income fields visible yet")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying fields: {e}")
            return False
    
    async def fill_income_fields(self, scenario: Dict) -> bool:
        """Fill the income fields based on employment type."""
        try:
            print("💰 Filling income fields...")
            
            income_amount = scenario['applicant1_income']
            
            if scenario['applicant1_employment'] == 'employed':
                return await self.fill_employed_income(income_amount)
            else:
                return await self.fill_self_employed_income(income_amount)
                
        except Exception as e:
            print(f"❌ Error filling income: {e}")
            return False
    
    async def fill_employed_income(self, income_amount: int) -> bool:
        """Fill employed income fields."""
        try:
            print(f"💼 Filling employed income: £{income_amount:,}")
            
            # Look for employed income fields
            income_selectors = [
                'input[name*="income_amount"]',
                'input[name*="basic_salary"]',
                'input[name*="employed_basic_salary"]'
            ]
            
            filled = False
            for selector in income_selectors:
                try:
                    field = await self.page.query_selector(selector)
                    if field and await field.is_visible():
                        await field.fill(str(income_amount))
                        print(f"✅ Filled {selector} with £{income_amount:,}")
                        filled = True
                        break
                except:
                    continue
            
            if not filled:
                print("❌ Could not find visible employed income field")
            
            return filled
            
        except Exception as e:
            print(f"❌ Error filling employed income: {e}")
            return False
    
    async def fill_self_employed_income(self, income_amount: int) -> bool:
        """Fill self-employed income fields following specified pattern."""
        try:
            print(f"🏢 Filling self-employed income: £{income_amount:,}")
            
            # Self-employed income pattern:
            # Year 1 (current): full amount
            # Year 2: half amount  
            # Year 3: 0
            year1_amount = income_amount
            year2_amount = income_amount // 2
            year3_amount = 0
            
            print(f"   Year 1 (current): £{year1_amount:,}")
            print(f"   Year 2: £{year2_amount:,}")
            print(f"   Year 3: £{year3_amount:,}")
            
            # Look for self-employed income fields (net profit)
            income_fields = [
                ('input[name*="net_profit"][name*="year_1"], input[name*="net_profit"][name*="last"]', year1_amount),
                ('input[name*="net_profit"][name*="year_2"]', year2_amount),
                ('input[name*="net_profit"][name*="year_3"]', year3_amount)
            ]
            
            filled_count = 0
            for selector, amount in income_fields:
                try:
                    field = await self.page.query_selector(selector)
                    if field and await field.is_visible():
                        await field.fill(str(amount))
                        print(f"✅ Filled {selector} with £{amount:,}")
                        filled_count += 1
                except Exception as e:
                    print(f"⚠️ Could not fill {selector}: {e}")
            
            # Set time in business: 2 years 0 months
            await self.set_time_in_business()
            
            print(f"✅ Filled {filled_count} self-employed income fields")
            return filled_count > 0
            
        except Exception as e:
            print(f"❌ Error filling self-employed income: {e}")
            return False
    
    async def set_time_in_business(self) -> bool:
        """Set time in business to 2 years 0 months for self-employed."""
        try:
            print("📅 Setting time in business: 2 years 0 months")
            
            # Look for time in business dropdowns
            years_select = await self.page.query_selector('select[name*="business"][name*="year"]')
            if years_select:
                await years_select.select_option('2')
                print("✅ Set business years to 2")
            
            months_select = await self.page.query_selector('select[name*="business"][name*="month"]')
            if months_select:
                await months_select.select_option('0')
                print("✅ Set business months to 0")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting time in business: {e}")
            return False
    
    async def fill_remaining_required_fields(self, scenario: Dict) -> bool:
        """Fill any remaining required fields (red asterisks)."""
        try:
            print("📋 Filling remaining required fields...")
            
            # Common required fields with sensible defaults
            required_defaults = [
                # Personal details
                ('select[name*="marital"]', 'Single'),
                ('select[name*="country"]', 'United Kingdom'),
                ('select[name*="dependent"]', '0'),
                
                # Property details
                ('select[name*="property_type"]', 'House'),
                ('select[name*="tenure"]', 'Freehold'),
                ('select[name*="new_build"]', 'No'),
                ('select[name*="main_residence"]', 'Yes'),
                
                # Financial
                ('input[name*="council_tax"]', '150'),
                ('input[name*="building_insurance"]', '50'),
                
                # Set commitments to 0
                ('input[name*="credit_card"]', '0'),
                ('input[name*="overdraft"]', '0'),
                ('input[name*="unsecured_loan"]', '0'),
                ('input[name*="secured_loan"]', '0'),
            ]
            
            for selector, value in required_defaults:
                try:
                    field = await self.page.query_selector(selector)
                    if field and await field.is_visible():
                        if selector.startswith('select'):
                            await field.select_option(value)
                        else:
                            await field.fill(value)
                        print(f"✅ Set {selector}")
                except:
                    continue  # Field might not exist or be required
            
            print("✅ Required fields completed")
            return True
            
        except Exception as e:
            print(f"❌ Error filling required fields: {e}")
            return False
    
    async def submit_and_extract_results(self, scenario: Dict) -> Dict[str, float]:
        """Submit form and extract results."""
        try:
            print("🚀 Submitting form and extracting results...")
            
            # Take screenshot before submission
            await self.page.screenshot(path=f"before_submit_{scenario['scenario_id']}.png")
            
            # Submit the form
            submit_button = await self.page.query_selector('button[type="submit"]')
            if submit_button:
                await submit_button.click()
                print("📤 Form submitted")
                
                # Wait for results page to load
                await self.page.wait_for_timeout(10000)
                await self.page.wait_for_load_state("networkidle", timeout=30000)
                
                # Take screenshot of results
                await self.page.screenshot(path=f"results_{scenario['scenario_id']}.png")
                print(f"📸 Results screenshot saved")
                
                # Extract lender results
                results = await self.extract_lender_results()
                return results
            else:
                print("❌ No submit button found")
                return {}
                
        except Exception as e:
            print(f"❌ Error submitting form: {e}")
            return {}
    
    async def extract_lender_results(self) -> Dict[str, float]:
        """Extract lender results from the results page."""
        try:
            print("📊 Extracting lender results...")
            results = {}
            
            # Get page content
            page_text = await self.page.text_content('body')
            
            # Try to find results in tables first
            tables = await self.page.query_selector_all('table')
            
            for table in tables:
                table_text = await table.text_content()
                
                # Check if this table contains lender information
                lender_count = sum(1 for lender in self.target_lenders if lender.lower() in table_text.lower())
                
                if lender_count >= 3:  # Table likely contains lender results
                    print(f"Found results table with {lender_count} lenders")
                    
                    rows = await table.query_selector_all('tr')
                    for row in rows:
                        row_text = await row.text_content()
                        
                        # Check each target lender
                        for lender in self.target_lenders:
                            if lender.lower() in row_text.lower():
                                # Extract amounts from row
                                amounts = re.findall(r'£[\d,]+', row_text)
                                if amounts:
                                    # Take largest amount as max borrowing
                                    max_amount = 0
                                    for amount_str in amounts:
                                        try:
                                            amount = float(amount_str.replace('£', '').replace(',', ''))
                                            if amount > max_amount and amount > 1000:
                                                max_amount = amount
                                        except:
                                            continue
                                    
                                    if max_amount > 0:
                                        results[lender] = max_amount
                                        print(f"✅ {lender}: £{max_amount:,.0f}")
                    
                    if results:
                        break  # Found results in this table
            
            # If no table results, try text parsing
            if not results:
                print("No table results found, trying text parsing...")
                
                for lender in self.target_lenders:
                    pattern = rf'{re.escape(lender)}.*?£([\d,]+)'
                    matches = re.findall(pattern, page_text, re.IGNORECASE | re.DOTALL)
                    
                    if matches:
                        amounts = [float(match.replace(',', '')) for match in matches]
                        max_amount = max(amounts)
                        if max_amount > 1000:
                            results[lender] = max_amount
                            print(f"✅ {lender}: £{max_amount:,.0f} (text)")
            
            print(f"📈 Extracted {len(results)} lender results")
            return results
            
        except Exception as e:
            print(f"❌ Error extracting results: {e}")
            return {}
    
    async def run_scenario(self, scenario: Dict) -> Dict[str, float]:
        """Run complete scenario with proper step-by-step workflow."""
        try:
            print(f"\n🎯 === RUNNING SCENARIO: {scenario['scenario_id']} ===")
            print(f"Type: {scenario['applicant_type']}")
            print(f"Income: £{scenario['applicant1_income']:,}")
            print(f"Employment: {scenario['applicant1_employment']}")
            
            # Step-by-step workflow
            steps = [
                ("Create new case", lambda: self.create_new_case(scenario)),
                ("Fill basic details", lambda: self.fill_required_basic_details(scenario)),
                ("Set property/loan defaults", lambda: self.set_property_and_loan_defaults()),
                ("Set number of applicants", lambda: self.set_number_of_applicants(scenario)),
                ("Set employment status", lambda: self.set_employment_status_and_unlock_income(scenario)),
                ("Fill income fields", lambda: self.fill_income_fields(scenario)),
                ("Fill remaining required fields", lambda: self.fill_remaining_required_fields(scenario)),
                ("Submit and extract results", lambda: self.submit_and_extract_results(scenario))
            ]
            
            for step_name, step_func in steps:
                print(f"\n--- {step_name.upper()} ---")
                result = await step_func()
                
                if step_name == "Submit and extract results":
                    # This step returns results, not boolean
                    return result if result else {}
                elif not result:
                    print(f"❌ Step '{step_name}' failed")
                    return {}
                
                # Brief pause between steps
                await self.page.wait_for_timeout(1000)
            
            return {}
            
        except Exception as e:
            print(f"❌ Error running scenario: {e}")
            return {}
    
    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()


# Test function
async def test_final_automation():
    """Test the final automation with correct workflow."""
    mbt = MBTAutomationFinalV2()
    
    try:
        # Start browser (non-headless for debugging)
        await mbt.start_browser(headless=False)
        
        if not await mbt.login():
            print("Login failed")
            return
        
        # Test scenarios
        test_scenarios = [
            {
                'scenario_id': 'joint_vanilla_40k',
                'scenario_type': 'vanilla',
                'applicant_type': 'joint',
                'applicant1_income': 40000,
                'applicant2_income': 40000,
                'applicant1_employment': 'employed',
                'applicant2_employment': 'employed',
                'age': 30,
                'term': 35
            },
            {
                'scenario_id': 'single_self_employed_40k',
                'scenario_type': 'self_employed',
                'applicant_type': 'single',
                'applicant1_income': 40000,
                'applicant2_income': None,
                'applicant1_employment': 'self_employed',
                'applicant2_employment': None,
                'age': 30,
                'term': 35
            }
        ]
        
        all_results = {}
        
        for scenario in test_scenarios:
            print(f"\n{'='*60}")
            results = await mbt.run_scenario(scenario)
            
            if results:
                all_results[scenario['scenario_id']] = results
                print(f"\n📊 SUCCESS - {scenario['scenario_id']}:")
                for lender, amount in results.items():
                    print(f"   {lender}: £{amount:,.0f}")
            else:
                print(f"\n❌ FAILED - {scenario['scenario_id']}: No results")
            
            # Brief pause between scenarios
            await asyncio.sleep(3)
        
        print(f"\n🎉 FINAL SUMMARY:")
        print(f"Completed {len(all_results)} out of {len(test_scenarios)} scenarios")
        
        for scenario_id, results in all_results.items():
            print(f"\n{scenario_id}: {len(results)} lenders")
    
    finally:
        print("\n⏳ Keeping browser open for inspection...")
        await asyncio.sleep(30)
        await mbt.close()


if __name__ == "__main__":
    asyncio.run(test_final_automation())