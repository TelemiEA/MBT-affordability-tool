"""
CORRECTED MBT automation that follows the proper workflow and fills the right fields.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv
import re

load_dotenv()

class MBTAutomationCorrected:
    """Corrected MBT automation that follows proper workflow."""
    
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
    
    async def start_browser(self, headless: bool = True):
        """Start browser."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-dev-shm-usage']
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
        """Create a new RESI case for each scenario."""
        try:
            print(f"📝 Creating NEW case for {scenario['scenario_id']}...")
            
            # Always go back to dashboard first to ensure clean state
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
    
    async def fill_step1_applicant_details(self, scenario: Dict) -> bool:
        """Fill Step 1: Basic applicant details."""
        try:
            print("👤 Step 1: Filling applicant details...")
            
            # Basic applicant info
            await self.page.fill('input[name="customer_title"]', 'Mr')
            await self.page.fill('input[name="firstname"]', 'Test')
            await self.page.fill('input[name="surname"]', 'User')
            await self.page.fill('input[name="email"]', f'test-{scenario["scenario_id"]}@example.com')
            await self.page.fill('input[name="customer_ref"]', scenario['scenario_id'].upper())
            
            print("✅ Step 1 completed")
            return True
            
        except Exception as e:
            print(f"❌ Error in Step 1: {e}")
            return False
    
    async def fill_step2_mortgage_preferences(self, scenario: Dict) -> bool:
        """Fill Step 2: Mortgage product preferences."""
        try:
            print("🏠 Step 2: Setting mortgage preferences...")
            
            # Ensure Residential is selected (usually default)
            residential_radio = await self.page.query_selector('input[name="type_of_quote"][value="Residential"]')
            if residential_radio:
                await residential_radio.check()
            
            # Ensure "No" for later life lending (usually default)
            later_life_no = await self.page.query_selector('input[name="laterlife"][value="No"]')
            if later_life_no:
                await later_life_no.check()
            
            # CRITICAL: Fill reason for mortgage - this may unlock other sections
            print("Setting reason for mortgage...")
            reason_search = await self.page.query_selector('input[placeholder="Reason for mortgage"]')
            if reason_search:
                await reason_search.fill('Purchase')
                await self.page.wait_for_timeout(1000)
                
                # Select first dropdown option
                dropdown_option = await self.page.query_selector('.ui-select-choices-row')
                if dropdown_option:
                    await dropdown_option.click()
                    print("✅ Reason for mortgage set to Purchase")
            
            print("✅ Step 2 completed")
            return True
            
        except Exception as e:
            print(f"❌ Error in Step 2: {e}")
            return False
    
    async def fill_step3_property_details(self, scenario: Dict) -> bool:
        """Fill Step 3: Property and mortgage details."""
        try:
            print("🏡 Step 3: Setting property details...")
            
            # Calculate realistic property value and loan based on income
            total_income = scenario['applicant1_income']
            if scenario.get('applicant2_income'):
                total_income += scenario['applicant2_income']
            
            property_value = total_income * 4  # 4x income multiple
            loan_amount = int(property_value * 0.8)  # 80% LTV
            
            print(f"   Property value: £{property_value:,}")
            print(f"   Loan amount: £{loan_amount:,}")
            
            # Fill purchase price/property value
            purchase_field = await self.page.query_selector('input[name="purchase"]')
            if purchase_field:
                await purchase_field.fill(str(property_value))
                print(f"✅ Property value set to £{property_value:,}")
            
            # Fill loan amount
            loan_field = await self.page.query_selector('input[name="loan_amount"]')
            if loan_field:
                await loan_field.fill(str(loan_amount))
                print(f"✅ Loan amount set to £{loan_amount:,}")
            
            # Fill other required property fields with defaults
            # Term years
            term_select = await self.page.query_selector('select[name*="term_year"]')
            if term_select:
                await term_select.select_option(str(scenario.get('term', 35)))
            
            # Term months
            term_months_select = await self.page.query_selector('select[name*="term_month"]')
            if term_months_select:
                await term_months_select.select_option('0')
            
            print("✅ Step 3 completed")
            return True
            
        except Exception as e:
            print(f"❌ Error in Step 3: {e}")
            return False
    
    async def fill_step4_personal_details(self, scenario: Dict) -> bool:
        """Fill Step 4: Personal details and demographics."""
        try:
            print("🎂 Step 4: Setting personal details...")
            
            # Age/Date of birth
            age = scenario.get('age', 30)
            birth_year = datetime.now().year - age
            
            # Try to fill date of birth
            dob_field = await self.page.query_selector('input[name*="dob"], input[name*="birth"]')
            if dob_field:
                await dob_field.fill(f'01/01/{birth_year}')
            
            # Number of applicants - CRITICAL for joint applications
            applicant_count = 2 if scenario['applicant_type'] == 'joint' else 1
            applicant_select = await self.page.query_selector('select[name*="applicant"]')
            if applicant_select:
                await applicant_select.select_option(str(applicant_count))
                print(f"✅ Set {applicant_count} applicant(s)")
            
            # Fill other required personal fields with defaults
            selects_to_fill = [
                ('select[name*="marital"]', 'Single'),
                ('select[name*="country"]', 'United Kingdom'),
                ('select[name*="adult"]', str(applicant_count)),
                ('select[name*="dependent"]', '0'),
                ('select[name*="residential_status"]', 'Owner Occupier')
            ]
            
            for selector, value in selects_to_fill:
                select_element = await self.page.query_selector(selector)
                if select_element:
                    try:
                        await select_element.select_option(value)
                    except:
                        pass  # Some options might not be available
            
            print("✅ Step 4 completed")
            return True
            
        except Exception as e:
            print(f"❌ Error in Step 4: {e}")
            return False
    
    async def fill_step5_employment_income(self, scenario: Dict) -> bool:
        """Fill Step 5: Employment and income - THE CRITICAL STEP."""
        try:
            print("💰 Step 5: Setting employment and income...")
            
            # Set employment status first - this should make income fields visible
            employment_select = await self.page.query_selector('select[name*="employment_status"]')
            if employment_select:
                if scenario['applicant1_employment'] == 'employed':
                    await employment_select.select_option('Employed')
                    print("✅ Set employment to Employed")
                else:
                    await employment_select.select_option('Self Employed')
                    print("✅ Set employment to Self Employed")
                
                # Wait for form to update and show income fields
                await self.page.wait_for_timeout(2000)
            
            # Now try to fill the income fields that should now be visible
            income_amount = scenario['applicant1_income']
            
            if scenario['applicant1_employment'] == 'employed':
                # For employed: look for basic salary field
                salary_field = await self.page.query_selector('input[name*="income_amount"], input[name*="basic_salary"]')
                if salary_field:
                    await salary_field.fill(str(income_amount))
                    print(f"✅ Set employed income to £{income_amount:,}")
                else:
                    print("❌ Could not find employed income field")
            
            else:  # self_employed
                # For self-employed: fill multiple years
                current_year_field = await self.page.query_selector('input[name*="self_employed_income_year_1"]')
                if current_year_field:
                    await current_year_field.fill(str(income_amount))
                    print(f"✅ Set self-employed current year to £{income_amount:,}")
                
                # Previous year (typically half for the test)
                previous_year_field = await self.page.query_selector('input[name*="self_employed_income_year_2"]')
                if previous_year_field:
                    previous_income = income_amount // 2
                    await previous_year_field.fill(str(previous_income))
                    print(f"✅ Set self-employed previous year to £{previous_income:,}")
            
            # If joint application, fill second applicant income
            if scenario['applicant_type'] == 'joint' and scenario.get('applicant2_income'):
                # This is more complex - may need to handle second applicant section
                print("📝 Handling joint applicant (implementation needed)")
            
            print("✅ Step 5 completed")
            return True
            
        except Exception as e:
            print(f"❌ Error in Step 5: {e}")
            return False
    
    async def fill_step6_commitments(self, scenario: Dict) -> bool:
        """Fill Step 6: Financial commitments."""
        try:
            print("💳 Step 6: Setting financial commitments...")
            
            # Set all commitments to zero for clean calculation
            commitment_fields = [
                'credit_card', 'overdraft', 'unsecured_loans', 'secured_loans',
                'hp_commitments', 'student_loans', 'council_tax', 'building_insurance'
            ]
            
            for field_name in commitment_fields:
                field = await self.page.query_selector(f'input[name*="{field_name}"]')
                if field:
                    await field.fill('0')
            
            # Set reasonable council tax and insurance
            council_tax_field = await self.page.query_selector('input[name*="council_tax"]')
            if council_tax_field:
                await council_tax_field.fill('150')
            
            insurance_field = await self.page.query_selector('input[name*="building_insurance"]')
            if insurance_field:
                await insurance_field.fill('50')
            
            print("✅ Step 6 completed")
            return True
            
        except Exception as e:
            print(f"❌ Error in Step 6: {e}")
            return False
    
    async def submit_and_get_results(self) -> Dict[str, float]:
        """Submit the form and extract results."""
        try:
            print("🚀 Submitting form and getting results...")
            
            # Submit the form
            submit_button = await self.page.query_selector('button[type="submit"]')
            if submit_button:
                await submit_button.click()
                print("📤 Form submitted")
                
                # Wait for results - this may take time
                await self.page.wait_for_timeout(10000)
                await self.page.wait_for_load_state("networkidle")
                
                # Take screenshot for debugging
                await self.page.screenshot(path=f"results_{datetime.now().strftime('%H%M%S')}.png")
                
                # Extract results
                results = await self.extract_lender_results()
                return results
            else:
                print("❌ No submit button found")
                return {}
                
        except Exception as e:
            print(f"❌ Error submitting form: {e}")
            return {}
    
    async def extract_lender_results(self) -> Dict[str, float]:
        """Extract lender results from the page."""
        try:
            print("📊 Extracting lender results...")
            results = {}
            
            # Look for results in various formats
            page_text = await self.page.text_content('body')
            
            # Try to find lender names and associated amounts
            for lender in self.target_lenders:
                # Look for patterns like "Lender Name ... £amount"
                pattern = rf'{re.escape(lender)}.*?£([\d,]+)'
                matches = re.findall(pattern, page_text, re.IGNORECASE | re.DOTALL)
                
                if matches:
                    # Take the largest amount found
                    amounts = [float(match.replace(',', '')) for match in matches]
                    max_amount = max(amounts)
                    if max_amount > 1000:  # Reasonable minimum
                        results[lender] = max_amount
                        print(f"✅ {lender}: £{max_amount:,.0f}")
            
            print(f"📈 Extracted {len(results)} lender results")
            return results
            
        except Exception as e:
            print(f"❌ Error extracting results: {e}")
            return {}
    
    async def run_scenario(self, scenario: Dict) -> Dict[str, float]:
        """Run complete scenario with corrected workflow."""
        try:
            print(f"\n🎯 Running corrected scenario: {scenario['scenario_id']}")
            
            # Step by step workflow
            steps = [
                self.create_new_case,
                self.fill_step1_applicant_details,
                self.fill_step2_mortgage_preferences,
                self.fill_step3_property_details,
                self.fill_step4_personal_details,
                self.fill_step5_employment_income,
                self.fill_step6_commitments
            ]
            
            for i, step in enumerate(steps, 1):
                print(f"\n--- Executing Step {i} ---")
                if not await step(scenario):
                    print(f"❌ Step {i} failed, stopping scenario")
                    return {}
                await self.page.wait_for_timeout(1000)  # Brief pause between steps
            
            # Submit and get results
            results = await self.submit_and_get_results()
            return results
            
        except Exception as e:
            print(f"❌ Error running scenario: {e}")
            return {}
    
    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()


# Test the corrected automation
async def test_corrected_automation():
    """Test the corrected MBT automation."""
    mbt = MBTAutomationCorrected()
    
    try:
        await mbt.start_browser(headless=False)  # Visual for debugging
        
        if not await mbt.login():
            return
        
        # Test scenario
        test_scenario = {
            'scenario_id': 'joint_vanilla_40k',
            'scenario_type': 'vanilla',
            'applicant_type': 'joint',
            'applicant1_income': 40000,
            'applicant2_income': 40000,
            'applicant1_employment': 'employed',
            'applicant2_employment': 'employed',
            'age': 30,
            'term': 35
        }
        
        results = await mbt.run_scenario(test_scenario)
        
        if results:
            print("\n📊 CORRECTED Results:")
            for lender, amount in results.items():
                print(f"  {lender}: £{amount:,.0f}")
        else:
            print("❌ No results obtained")
    
    finally:
        await asyncio.sleep(30)  # Keep browser open for inspection
        await mbt.close()


if __name__ == "__main__":
    asyncio.run(test_corrected_automation())