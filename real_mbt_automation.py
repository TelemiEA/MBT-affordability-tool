"""
Real MBT Automation - Gets actual numbers from MBT
Properly clears income fields and inputs new amounts
"""

import asyncio
import os
import json
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

# Case mapping - verified working
CASE_REFERENCES = {
    "E.Single": "QX002187461",  # Single employed
    "E.Joint": "QX002187450",   # Joint employed  
    "S.Single": "QX002187335",  # Single self-employed
    "S.Joint": "QX002187301",   # Joint self-employed + employed
    # Credit commitment cases - QX reference numbers for C.* cases
    "C.E-Single": "QX002304221",    # Single employed with commitments  
    "C.E-Joint": "QX002304261",     # Joint employed with commitments
    "C.Self-Single": "QX002304287", # Single self-employed with commitments
    "C.Self-Joint": "QX002304304"   # Joint self-employed with commitments
}

class RealMBTAutomation:
    """Real MBT automation that gets actual lender results."""
    
    def __init__(self):
        self.browser = None
        self.page = None
    
    async def start_browser(self):
        """Start browser session."""
        try:
            self.playwright = await async_playwright().start()
            
            # Cloud-friendly browser configuration
            browser_args = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ]
            
            # Auto-detect environment (local vs cloud)
            import os
            is_production = os.getenv('RAILWAY_ENVIRONMENT_NAME') or os.getenv('PORT')
            
            self.browser = await self.playwright.chromium.launch(
                headless=bool(is_production),  # Headless in production, visible locally
                slow_mo=0 if is_production else 1000,  # No slow mode in production
                args=browser_args if is_production else []
            )
            self.page = await self.browser.new_page()
            
            print(f"🌐 Browser started ({'headless' if is_production else 'visible'} mode)")
            
        except Exception as e:
            print(f"❌ Browser startup failed: {e}")
            # Re-raise with more context
            raise Exception(f"Failed to start browser for MBT automation: {e}")
        
    async def close(self):
        """Close browser session."""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def login(self):
        """Login to MBT."""
        try:
            print("🔐 Logging into MBT...")
            await self.page.goto("https://mortgagebrokertools.co.uk/signin", timeout=30000)
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Clear and fill email
            await self.page.click('input[name="email"]')
            await self.page.keyboard.press('Control+a')  # Select all
            await self.page.keyboard.press('Delete')     # Delete existing
            await self.page.type('input[name="email"]', os.getenv("MBT_USERNAME"))
            
            # Clear and fill password
            await self.page.click('input[name="password"]')
            await self.page.keyboard.press('Control+a')  # Select all
            await self.page.keyboard.press('Delete')     # Delete existing
            await self.page.type('input[name="password"]', os.getenv("MBT_PASSWORD"))
            
            await self.page.click('input[type="submit"]')
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            print("✅ Login successful")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    async def run_single_scenario(self, case_type, income):
        """Run a single scenario and get real results."""
        try:
            case_reference = CASE_REFERENCES[case_type]
            print(f"\\n🎯 Running scenario: {case_type} with income £{income:,}")
            
            # Navigate to dashboard
            await self.page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes', timeout=30000)
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            # Click on the case reference to open it
            await self.page.click(f'text={case_reference}', timeout=10000)
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await self.page.wait_for_timeout(3000)
            print(f"   ✅ Opened case: {case_reference}")
            
            # Navigate to income section
            await self.navigate_to_income_section()
            
            # Update income based on case type
            if case_type.startswith('E'):  # Employed
                if case_type.endswith('Joint'):  # Joint employed
                    income_updated = await self.update_joint_employed_income_properly(income)
                else:  # Single employed
                    income_updated = await self.update_employed_income_properly(income)
            elif case_type.startswith('S'):  # Self-employed
                if case_type.endswith('Joint'):  # Joint self-employed + employed
                    income_updated = await self.update_joint_self_employed_income_properly(income)
                else:  # Single self-employed
                    income_updated = await self.update_self_employed_income_properly(income)
            elif case_type.startswith('C'):  # Credit commitment cases
                if 'E-' in case_type:  # Credit commitment employed cases
                    if 'Joint' in case_type:
                        income_updated = await self.update_joint_employed_income_properly(income)
                    else:
                        income_updated = await self.update_employed_income_properly(income)
                else:  # Credit commitment self-employed cases
                    if 'Joint' in case_type:
                        income_updated = await self.update_joint_self_employed_income_properly(income)
                    else:
                        income_updated = await self.update_self_employed_income_properly(income)
                
                # Update credit commitments with correct amounts (1% and 10% of income)
                if income_updated:
                    credit_updated = await self.update_credit_commitments(income, case_type)
                    income_updated = income_updated and credit_updated
            
            if income_updated:
                print("   ✅ Income updated successfully")
                # After income update, results should appear at bottom of SAME page
                # DO NOT navigate away - just extract results from current page
                lenders_data = await self.run_search_and_extract_results(case_type, income)
            else:
                print("   ❌ Income update failed")
                lenders_data = {}
            
            return {
                'case_type': case_type,
                'case_reference': case_reference,
                'income': income,
                'lenders_data': lenders_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"   ❌ Scenario error: {e}")
            return None
    
    async def navigate_to_income_section(self):
        """Navigate through form sections to reach income section."""
        try:
            # The form may have multiple sections, navigate through them
            for attempt in range(5):  # Try up to 5 section navigations
                page_text = await self.page.text_content('body')
                
                # Check if we're in income section
                if any(term in page_text.lower() for term in ['annual basic salary', 'net profit', 'income']):
                    print("   ✅ Reached income section")
                    break
                
                # Look for Next/Continue buttons
                next_buttons = await self.page.query_selector_all('button, input[type="submit"]')
                for button in next_buttons:
                    try:
                        text = await button.text_content() or ''
                        if any(term in text.lower() for term in ['next', 'continue', 'save']):
                            await button.click()
                            await self.page.wait_for_load_state("networkidle", timeout=10000)
                            await self.page.wait_for_timeout(2000)
                            print(f"   ✅ Clicked: {text}")
                            break
                    except:
                        continue
                        
        except Exception as e:
            print(f"   ⚠️ Navigation warning: {e}")
    
    async def update_employed_income_properly(self, income):
        """Update employed income with proper clearing."""
        try:
            print(f"   💰 Updating employed income to £{income:,}")
            
            # Take screenshot before
            await self.page.screenshot(path="before_income_update.png")
            
            # Find annual basic salary field
            inputs = await self.page.query_selector_all('input[type="text"], input[type="number"]')
            
            for input_field in inputs:
                try:
                    if not await input_field.is_visible():
                        continue
                    
                    # Get context about the field
                    parent = await input_field.query_selector('..')
                    if parent:
                        parent_text = await parent.text_content() or ''
                        
                        if 'annual basic salary' in parent_text.lower():
                            # AGGRESSIVELY CLEAR EVERY SINGLE CHARACTER
                            await input_field.click()
                            await self.page.wait_for_timeout(500)
                            
                            # Method 1: Select all and delete multiple times
                            for _ in range(3):
                                await self.page.keyboard.press('Control+a')
                                await self.page.keyboard.press('Delete')
                                await self.page.wait_for_timeout(200)
                            
                            # Method 2: Backspace everything (up to 20 characters)
                            for _ in range(20):
                                await self.page.keyboard.press('Backspace')
                                await self.page.wait_for_timeout(50)
                            
                            # Method 3: Use fill with empty string
                            await input_field.fill('')
                            await self.page.wait_for_timeout(500)
                            
                            # Method 4: More backspaces to be absolutely sure
                            for _ in range(10):
                                await self.page.keyboard.press('Backspace')
                                await self.page.wait_for_timeout(50)
                            
                            # Verify field is empty
                            current_value = await input_field.input_value()
                            print(f"   🔍 Field value after clearing: '{current_value}'")
                            
                            # If still not empty, try more aggressive clearing
                            if current_value and current_value.strip():
                                print("   ⚠️ Field not empty, trying more aggressive clearing...")
                                await input_field.clear()  # Playwright's clear method
                                await self.page.wait_for_timeout(500)
                                
                                # Final backspace assault
                                for _ in range(30):
                                    await self.page.keyboard.press('Backspace')
                                    await self.page.wait_for_timeout(30)
                            
                            # Now type the new value
                            await input_field.type(str(income), delay=100)
                            await input_field.press('Tab')
                            
                            # Verify the value was set
                            new_value = await input_field.input_value()
                            print(f"   ✅ Updated salary field to: {new_value}")
                            
                            await self.page.screenshot(path="after_income_update.png")
                            return True
                            
                except Exception as e:
                    print(f"   ⚠️ Error with input field: {e}")
                    continue
            
            print("   ⚠️ Could not find annual basic salary field")
            return False
            
        except Exception as e:
            print(f"   ❌ Error updating employed income: {e}")
            return False
    
    async def update_self_employed_income_properly(self, income):
        """Update self-employed income with proper clearing."""
        try:
            print(f"   💰 Updating self-employed income to £{income:,}")
            
            # For self-employed: last year = income, two years = income/2
            last_year_profit = income
            two_year_profit = income // 2
            
            await self.page.screenshot(path="before_self_employed_update.png")
            
            inputs = await self.page.query_selector_all('input[type="text"], input[type="number"]')
            
            last_year_updated = False
            two_year_updated = False
            
            for input_field in inputs:
                try:
                    if not await input_field.is_visible():
                        continue
                    
                    parent = await input_field.query_selector('..')
                    if parent:
                        parent_text = await parent.text_content() or ''
                        combined = parent_text.lower()
                        
                        # Last year profit
                        if not last_year_updated and 'profit' in combined and ('last' in combined or 'current' in combined):
                            # AGGRESSIVELY CLEAR EVERY SINGLE CHARACTER
                            await input_field.click()
                            await self.page.wait_for_timeout(500)
                            
                            # Multiple clearing methods
                            for _ in range(3):
                                await self.page.keyboard.press('Control+a')
                                await self.page.keyboard.press('Delete')
                                await self.page.wait_for_timeout(200)
                            
                            for _ in range(20):
                                await self.page.keyboard.press('Backspace')
                                await self.page.wait_for_timeout(50)
                            
                            await input_field.fill('')
                            await self.page.wait_for_timeout(500)
                            
                            # Verify empty
                            current_value = await input_field.input_value()
                            print(f"   🔍 Last year field after clearing: '{current_value}'")
                            
                            if current_value and current_value.strip():
                                await input_field.clear()
                                for _ in range(30):
                                    await self.page.keyboard.press('Backspace')
                                    await self.page.wait_for_timeout(30)
                            
                            await input_field.type(str(last_year_profit), delay=100)
                            await input_field.press('Tab')
                            
                            new_value = await input_field.input_value()
                            print(f"   ✅ Updated last year profit to: {new_value}")
                            last_year_updated = True
                            continue
                        
                        # Two year profit
                        if not two_year_updated and 'profit' in combined and ('two' in combined or '2' in combined):
                            # AGGRESSIVELY CLEAR EVERY SINGLE CHARACTER
                            await input_field.click()
                            await self.page.wait_for_timeout(500)
                            
                            # Multiple clearing methods
                            for _ in range(3):
                                await self.page.keyboard.press('Control+a')
                                await self.page.keyboard.press('Delete')
                                await self.page.wait_for_timeout(200)
                            
                            for _ in range(20):
                                await self.page.keyboard.press('Backspace')
                                await self.page.wait_for_timeout(50)
                            
                            await input_field.fill('')
                            await self.page.wait_for_timeout(500)
                            
                            # Verify empty
                            current_value = await input_field.input_value()
                            print(f"   🔍 Two year field after clearing: '{current_value}'")
                            
                            if current_value and current_value.strip():
                                await input_field.clear()
                                for _ in range(30):
                                    await self.page.keyboard.press('Backspace')
                                    await self.page.wait_for_timeout(30)
                            
                            await input_field.type(str(two_year_profit), delay=100)
                            await input_field.press('Tab')
                            
                            new_value = await input_field.input_value()
                            print(f"   ✅ Updated two year profit to: {new_value}")
                            two_year_updated = True
                            continue
                            
                except Exception as e:
                    continue
            
            print(f"   📊 Self-employed fields updated: Last year: {last_year_updated}, Two year: {two_year_updated}")
            await self.page.screenshot(path="after_self_employed_update.png")
            return last_year_updated and two_year_updated
            
        except Exception as e:
            print(f"   ❌ Error updating self-employed income: {e}")
            return False
    
    async def update_joint_employed_income_properly(self, income):
        """Update both applicants' employed income for joint employed scenarios."""
        try:
            print(f"   💰 Updating JOINT employed income (TOTAL £{income:,}):")
            
            # Split income equally between applicants for joint employed
            applicant_income = income // 2
            print(f"       Each applicant gets: £{applicant_income:,} (split equally)")
            print(f"       ⚠️  VERIFY: Each applicant should get £{applicant_income:,}, NOT £{income:,}")
            
            await self.page.screenshot(path="before_joint_employed_update.png")
            
            inputs = await self.page.query_selector_all('input[type="text"], input[type="number"]')
            
            applicant1_updated = False
            applicant2_updated = False
            
            for input_field in inputs:
                try:
                    if not await input_field.is_visible():
                        continue
                    
                    # Get context about the field
                    parent = await input_field.query_selector('..')
                    if parent:
                        parent_text = await parent.text_content() or ''
                        combined_text = parent_text.lower()
                        
                        # Look for applicant 1 annual basic salary
                        if not applicant1_updated and 'annual basic salary' in combined_text and ('applicant 1' in combined_text or 'first applicant' in combined_text):
                            success = await self.clear_and_fill_income_field(input_field, applicant_income, "Applicant 1 salary")
                            if success:
                                applicant1_updated = True
                                continue
                        
                        # Look for applicant 2 annual basic salary  
                        if not applicant2_updated and 'annual basic salary' in combined_text and ('applicant 2' in combined_text or 'second applicant' in combined_text):
                            success = await self.clear_and_fill_income_field(input_field, applicant_income, "Applicant 2 salary")
                            if success:
                                applicant2_updated = True
                                continue
                                
                        # Fallback: if we find salary fields without clear applicant indicators, try to update them in order
                        if 'annual basic salary' in combined_text and not applicant1_updated:
                            success = await self.clear_and_fill_income_field(input_field, applicant_income, "First salary field (assuming Applicant 1)")
                            if success:
                                applicant1_updated = True
                                continue
                        
                        if 'annual basic salary' in combined_text and applicant1_updated and not applicant2_updated:
                            success = await self.clear_and_fill_income_field(input_field, applicant_income, "Second salary field (assuming Applicant 2)")
                            if success:
                                applicant2_updated = True
                                continue
                            
                except Exception as e:
                    print(f"   ⚠️ Error with input field: {e}")
                    continue
            
            print(f"   📊 Joint employed fields updated: Applicant 1: {applicant1_updated}, Applicant 2: {applicant2_updated}")
            await self.page.screenshot(path="after_joint_employed_update.png")
            return applicant1_updated and applicant2_updated
            
        except Exception as e:
            print(f"   ❌ Error updating joint employed income: {e}")
            return False
    
    async def update_joint_self_employed_income_properly(self, income):
        """Update applicant 1 (self-employed) and applicant 2 (employed) for joint self-employed scenarios."""
        try:
            # For joint self-employed scenarios, split the total income equally between both applicants:
            # Applicant 1 (self-employed): Gets half of total income for last year, quarter for two years ago
            # Applicant 2 (employed): Gets half of total income (split equally)
            applicant_income = income // 2  # Split total income equally between both applicants
            applicant2_salary = applicant_income  # Employed applicant gets half of total
            
            print(f"   💰 Updating JOINT self-employed income (TOTAL £{income:,}):")
            print(f"       Applicant 1 (self-employed): Last year £{applicant_income:,}, Two years £{applicant_income//2:,}")
            print(f"       Applicant 2 (employed): £{applicant2_salary:,}")
            print(f"       Both applicants split the £{income:,} total equally")
            
            last_year_profit = applicant_income  # Half of total income
            two_year_profit = applicant_income // 2  # Quarter of total income
            
            print(f"   🔍 DEBUG VALUES:")
            print(f"       total income: £{income:,}")
            print(f"       applicant_income (split): £{applicant_income:,}")
            print(f"       last_year_profit: £{last_year_profit:,}")
            print(f"       two_year_profit: £{two_year_profit:,}")
            print(f"       applicant2_salary: £{applicant2_salary:,}")
            
            await self.page.screenshot(path="before_joint_self_employed_update.png")
            
            inputs = await self.page.query_selector_all('input[type="text"], input[type="number"]')
            
            app1_last_year_updated = False
            app1_two_year_updated = False
            app2_salary_updated = False
            
            for input_field in inputs:
                try:
                    if not await input_field.is_visible():
                        continue
                    
                    parent = await input_field.query_selector('..')
                    if parent:
                        parent_text = await parent.text_content() or ''
                        combined = parent_text.lower()
                        
                        # Applicant 1 - Self-employed profit fields
                        if not app1_last_year_updated and 'profit' in combined and ('last' in combined or 'current' in combined) and ('applicant 1' in combined or 'first' in combined):
                            print(f"   🎯 FOUND last year field! Field text: '{combined[:100]}'")
                            print(f"   💰 INPUTTING SPLIT AMOUNT: £{last_year_profit:,} (THIS IS HALF OF £{income:,} TOTAL)")
                            print(f"   ⚠️  VERIFY: We are inputting £{last_year_profit:,}, NOT the full £{income:,}")
                            success = await self.clear_and_fill_income_field(input_field, last_year_profit, "Applicant 1 last year profit")
                            if success:
                                app1_last_year_updated = True
                                continue
                        
                        if not app1_two_year_updated and 'profit' in combined and ('two' in combined or '2' in combined) and ('applicant 1' in combined or 'first' in combined):
                            print(f"   🎯 FOUND two year field! Inputting: £{two_year_profit:,}")
                            success = await self.clear_and_fill_income_field(input_field, two_year_profit, "Applicant 1 two year profit")
                            if success:
                                app1_two_year_updated = True
                                continue
                        
                        # Applicant 2 - Employed salary
                        if not app2_salary_updated and 'annual basic salary' in combined and ('applicant 2' in combined or 'second' in combined):
                            print(f"   🎯 FOUND applicant 2 salary field!")
                            print(f"   💰 INPUTTING SPLIT AMOUNT: £{applicant2_salary:,} (THIS IS HALF OF £{income:,} TOTAL)")
                            print(f"   ⚠️  VERIFY: We are inputting £{applicant2_salary:,}, NOT the full £{income:,}")
                            success = await self.clear_and_fill_income_field(input_field, applicant2_salary, "Applicant 2 salary")
                            if success:
                                app2_salary_updated = True
                                continue
                        
                        # Fallback patterns for unclear labeling
                        if not app1_last_year_updated and 'profit' in combined and ('last' in combined or 'current' in combined):
                            success = await self.clear_and_fill_income_field(input_field, last_year_profit, "Last year profit (assuming Applicant 1)")
                            if success:
                                app1_last_year_updated = True
                                continue
                        
                        if not app1_two_year_updated and 'profit' in combined and ('two' in combined or '2' in combined):
                            success = await self.clear_and_fill_income_field(input_field, two_year_profit, "Two year profit (assuming Applicant 1)")
                            if success:
                                app1_two_year_updated = True
                                continue
                        
                        if not app2_salary_updated and 'annual basic salary' in combined and app1_last_year_updated:
                            success = await self.clear_and_fill_income_field(input_field, applicant2_salary, "Salary (assuming Applicant 2)")
                            if success:
                                app2_salary_updated = True
                                continue
                            
                except Exception as e:
                    continue
            
            print(f"   📊 Joint self-employed fields updated:")
            print(f"       App1 Last year: {app1_last_year_updated}, App1 Two year: {app1_two_year_updated}")
            print(f"       App2 Salary: {app2_salary_updated}")
            
            # FINAL VERIFICATION - Check what values are actually in the fields
            print(f"   🔍 FINAL VERIFICATION OF SPLIT INCOME:")
            print(f"       Original total income: £{income:,}")
            print(f"       Expected split amounts: £{applicant_income:,} each")
            if app1_last_year_updated:
                print(f"       ✅ App1 last year profit: UPDATED with £{last_year_profit:,}")
            if app1_two_year_updated:
                print(f"       ✅ App1 two year profit: UPDATED with £{two_year_profit:,}")
            if app2_salary_updated:
                print(f"       ✅ App2 salary: UPDATED with £{applicant2_salary:,}")
            
            await self.page.screenshot(path="after_joint_self_employed_update.png")
            return app1_last_year_updated and app1_two_year_updated and app2_salary_updated
            
        except Exception as e:
            print(f"   ❌ Error updating joint self-employed income: {e}")
            return False
    
    async def clear_and_fill_income_field(self, input_field, amount, field_description):
        """Helper method to clear and fill an income field with proper validation."""
        try:
            # AGGRESSIVELY CLEAR EVERY SINGLE CHARACTER
            await input_field.click()
            await self.page.wait_for_timeout(500)
            
            # Method 1: Select all and delete multiple times
            for _ in range(3):
                await self.page.keyboard.press('Control+a')
                await self.page.keyboard.press('Delete')
                await self.page.wait_for_timeout(200)
            
            # Method 2: Backspace everything (up to 20 characters)
            for _ in range(20):
                await self.page.keyboard.press('Backspace')
                await self.page.wait_for_timeout(50)
            
            # Method 3: Use fill with empty string
            await input_field.fill('')
            await self.page.wait_for_timeout(500)
            
            # Method 4: More backspaces to be absolutely sure
            for _ in range(10):
                await self.page.keyboard.press('Backspace')
                await self.page.wait_for_timeout(50)
            
            # Verify field is empty
            current_value = await input_field.input_value()
            print(f"   🔍 {field_description} after clearing: '{current_value}'")
            
            # If still not empty, try more aggressive clearing
            if current_value and current_value.strip():
                print(f"   ⚠️ {field_description} not empty, trying more aggressive clearing...")
                await input_field.clear()  # Playwright's clear method
                await self.page.wait_for_timeout(500)
                
                # Final backspace assault
                for _ in range(30):
                    await self.page.keyboard.press('Backspace')
                    await self.page.wait_for_timeout(30)
            
            # Now type the new value
            await input_field.type(str(amount), delay=100)
            await input_field.press('Tab')
            
            # Verify the value was set
            new_value = await input_field.input_value()
            print(f"   ✅ Updated {field_description} to: {new_value}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error updating {field_description}: {e}")
            return False
    
    async def navigate_through_form_sections(self):
        """Navigate through all form sections until we reach criteria search or results."""
        try:
            print("   🧭 Navigating through form sections...")
            
            max_attempts = 15  # Increased attempts to handle more form sections
            
            for attempt in range(max_attempts):
                # Take screenshot of current state
                await self.page.screenshot(path=f"form_section_{attempt + 1}.png")
                
                page_text = await self.page.text_content('body')
                current_url = self.page.url
                
                print(f"   📍 Section {attempt + 1}: {current_url}")
                
                # Check if we've reached criteria search or results
                if any(term in page_text.lower() for term in ['criteria search', 'lenders:', 'results', 'offers']):
                    print(f"   ✅ Reached target page at section {attempt + 1}")
                    break
                
                # Look for buttons to continue
                buttons = await self.page.query_selector_all('button, input[type="submit"]')
                clicked_something = False
                
                for button in buttons:
                    try:
                        if not await button.is_visible():
                            continue
                            
                        text = await button.text_content() or ''
                        html = await button.inner_html() or ''
                        classes = await button.get_attribute('class') or ''
                        
                        # Look for navigation buttons (Next, Continue, Save) OR green play buttons
                        is_navigation = any(term in text.lower() for term in ['next', 'continue', 'save', 'search'])
                        is_play_button = 'zmdi-play' in html or 'play' in classes.lower()
                        is_residential = 'residential' in text.lower()
                        
                        if is_navigation or is_play_button or is_residential:
                            print(f"   🎯 Clicking button: '{text.strip()}' (play: {is_play_button}, nav: {is_navigation})")
                            await button.click()
                            await self.page.wait_for_load_state("networkidle", timeout=30000)
                            await self.page.wait_for_timeout(3000)
                            clicked_something = True
                            break
                            
                    except Exception as e:
                        print(f"   ⚠️ Button click error: {e}")
                        continue
                
                if not clicked_something:
                    print(f"   ⚠️ No clickable buttons found at section {attempt + 1}")
                    break
            
            print("   ✅ Form navigation completed")
            
        except Exception as e:
            print(f"   ❌ Error navigating form sections: {e}")
    
    async def update_credit_commitments(self, income, case_type=None):
        """Add credit commitments: 1% current repayments, 10% balance on completion.
        For joint scenarios, uses only Applicant 1's portion (50% of total income)."""
        try:
            print(f"   💳 Adding credit commitments for income £{income:,}")
            
            # For joint scenarios, calculate commitments based on Applicant 1's portion only
            if case_type and (case_type.endswith('Joint') or 'Joint' in case_type):
                applicant1_income = int(income * 0.5)  # Assume 50/50 split for joint scenarios
                print(f"   👥 Joint scenario detected - using Applicant 1's portion: £{applicant1_income:,} (50% of total)")
                commitment_base = applicant1_income
            else:
                commitment_base = income
            
            # Calculate commitment amounts based on appropriate income
            current_repayments = int(commitment_base * 0.01)  # 1% of applicable income
            balance_on_completion = int(commitment_base * 0.10)  # 10% of applicable income
            
            print(f"   💰 Current repayments: £{current_repayments}")
            print(f"   💰 Balance on completion: £{balance_on_completion}")
            
            # Look for First-applicant loan commitments section
            page_text = await self.page.text_content('body')
            if 'first-applicant loan commitments' not in page_text.lower():
                # Navigate to loan commitments section
                await self.navigate_to_loan_commitments_section()
            
            # Find Unsecured loans section - current repayments field (left side)
            current_repayments_updated = await self.update_unsecured_current_repayments(current_repayments)
            
            # Find Unsecured loans section - balance on completion field (right side)  
            balance_updated = await self.update_unsecured_balance_on_completion(balance_on_completion)
            
            if current_repayments_updated and balance_updated:
                print("   ✅ Credit commitments updated successfully")
                return True
            else:
                print("   ❌ Failed to update credit commitments")
                return False
                
        except Exception as e:
            print(f"   ❌ Credit commitments error: {e}")
            return False
    
    async def navigate_to_loan_commitments_section(self):
        """Navigate to the First-applicant loan commitments section."""
        try:
            # Look for navigation buttons or sections that might lead to loan commitments
            for attempt in range(10):
                page_text = await self.page.text_content('body')
                
                if 'first-applicant loan commitments' in page_text.lower():
                    print("   ✅ Found loan commitments section")
                    return True
                
                # Look for next/continue buttons
                buttons = await self.page.query_selector_all('button, input[type="submit"], a')
                for button in buttons:
                    try:
                        button_text = await button.text_content() or ''
                        if any(term in button_text.lower() for term in ['next', 'continue', 'loan', 'commit']):
                            await button.click()
                            await self.page.wait_for_load_state("networkidle", timeout=10000)
                            await self.page.wait_for_timeout(2000)
                            print(f"   ✅ Clicked: {button_text}")
                            break
                    except:
                        continue
                        
        except Exception as e:
            print(f"   ⚠️ Navigation to loan commitments error: {e}")
            return False
    
    async def update_unsecured_current_repayments(self, amount):
        """Update current repayments field in Unsecured loans section."""
        try:
            print(f"   💰 Updating current repayments to £{amount}")
            
            # Look for input fields near "current repayments" and "unsecured loans"
            inputs = await self.page.query_selector_all('input[type="text"], input[type="number"]')
            
            for input_field in inputs:
                try:
                    if not await input_field.is_visible():
                        continue
                    
                    # Check context around the field
                    parent = await input_field.query_selector('..')
                    if parent:
                        parent_text = await parent.text_content() or ''
                        
                        # Look for field that contains both "current repayments" and "unsecured"
                        if ('current repayments' in parent_text.lower() and 
                            'unsecured' in parent_text.lower()):
                            
                            await self.clear_and_fill_income_field(input_field, amount, "current repayments")
                            return True
                            
                except Exception as e:
                    continue
            
            print("   ❌ Could not find current repayments field")
            return False
            
        except Exception as e:
            print(f"   ❌ Current repayments update error: {e}")
            return False
    
    async def update_unsecured_balance_on_completion(self, amount):
        """Update balance on completion field in Unsecured loans section."""
        try:
            print(f"   💰 Updating balance on completion to £{amount}")
            
            # Look for input fields near "balance on completion" and "unsecured loans"
            inputs = await self.page.query_selector_all('input[type="text"], input[type="number"]')
            
            for input_field in inputs:
                try:
                    if not await input_field.is_visible():
                        continue
                    
                    # Check context around the field
                    parent = await input_field.query_selector('..')
                    if parent:
                        parent_text = await parent.text_content() or ''
                        
                        # Look for field that contains both "balance on completion" and "unsecured"
                        if ('balance on completion' in parent_text.lower() and 
                            'unsecured' in parent_text.lower()):
                            
                            await self.clear_and_fill_income_field(input_field, amount, "balance on completion")
                            return True
                            
                except Exception as e:
                    continue
            
            print("   ❌ Could not find balance on completion field")
            return False
            
        except Exception as e:
            print(f"   ❌ Balance on completion update error: {e}")
            return False
    
    async def run_search_and_extract_results(self, case_type, income):
        """Run search and extract real lender results."""
        try:
            print("   🚀 FIRST PRIORITY: Click green button to trigger fresh calculation...")
            
            # CRITICAL: Click the green button FIRST to trigger new calculation
            calculation_triggered = await self.click_green_button_to_calculate()
            
            if calculation_triggered:
                print("   ✅ GREEN BUTTON CLICKED - Fresh calculation triggered!")
                
                # Calculate wait time based on scenario complexity - EXTREMELY conservative wait times
                base_wait = 180000  # Base 3 minutes (minimum after green button)
                income_multiplier = max(1.2, income / 30000)  # Extra time for higher incomes (more aggressive)
                joint_multiplier = 3.0 if case_type.endswith('Joint') else 1.5  # 3x time for joint, 1.5x for single
                
                total_wait = int(base_wait * income_multiplier * joint_multiplier)
                total_wait = min(total_wait, 600000)  # Cap at 10 minutes
                
                print(f"   🧮 Wait calculation: base={base_wait/1000}s × income_mult={income_multiplier:.1f} × joint_mult={joint_multiplier:.1f} = {total_wait/1000:.0f}s")
                
                print(f"   ⏳ Waiting {total_wait/1000:.0f} seconds for calculation (income: £{income:,}, joint: {case_type.endswith('Joint')})")
                await self.page.wait_for_timeout(total_wait)
                
                # Wait for all lenders to populate with progressive checking
                print("   🔍 Checking if all lenders have loaded...")
                await self.wait_for_all_lenders_to_load()
                
            else:
                print("   ❌ GREEN BUTTON NOT FOUND - This will extract old cached results!")
                # Still proceed but warn about cached results
                await self.page.wait_for_timeout(5000)
            
            # SECOND: Extract the results (should now be fresh if green button worked)
            print("   📊 Extracting results (should be fresh if green button was clicked)...")
            
            lenders_data = await self.extract_real_lender_data()
            
            # Aggressive retry logic if we didn't get enough lenders
            retry_count = 0
            max_retries = 3
            
            while lenders_data and len(lenders_data) < 12 and retry_count < max_retries:
                retry_count += 1
                print(f"   ⚠️ Only found {len(lenders_data)} lenders (retry {retry_count}/{max_retries})")
                print(f"   ⏳ Waiting 20 more seconds for lenders to populate...")
                await self.page.wait_for_timeout(20000)  # Wait 20 more seconds
                lenders_data = await self.extract_real_lender_data()
            
            if lenders_data:
                lender_count = len(lenders_data)
                print(f"   ✅ Results extracted! Found {lender_count} lenders")
                
                # Warn if we have fewer lenders than expected
                if lender_count < 12:
                    print(f"   ⚠️ Warning: Only {lender_count} lenders found (expected 12+)")
                    print("   💡 Consider increasing wait times for this scenario type")
                
                # Quick sanity check - verify results look reasonable for the income level
                gen_h_amount = lenders_data.get('Gen H', 0)
                if gen_h_amount > 0:
                    print(f"   🔍 Gen H affordability: £{gen_h_amount:,}")
                    
                    # For joint scenarios, we expect higher affordability than single scenarios
                    # This helps verify we're getting results for the correct income
                    
                return lenders_data
            else:
                print("   ❌ No results found after retries")
                return {}
            
        except Exception as e:
            print(f"   ❌ Error in search and extract: {e}")
            return {}
    
    async def click_green_button_to_calculate(self):
        """Click the green button to trigger affordability calculation."""
        try:
            print("   🎯 Looking for the green play button...")
            
            # Multiple selectors to find the green play button
            play_button_selectors = [
                '.zmdi-play',                    # The play icon that worked before
                'i.zmdi-play',                   # Play icon element
                'button .zmdi-play',             # Button containing play icon
                '[class*="zmdi-play"]',          # Any element with zmdi-play in class
                'button[class*="green"]',        # Green buttons
                'button[style*="green"]',        # Buttons with green styling
            ]
            
            # Also look for buttons with green text/content
            all_buttons = await self.page.query_selector_all('button, div[role="button"], a[role="button"]')
            
            for button in all_buttons:
                try:
                    if not await button.is_visible():
                        continue
                    
                    # Check button content and styling
                    text = (await button.text_content() or '').lower()
                    html = await button.inner_html()
                    classes = await button.get_attribute('class') or ''
                    
                    # Look for play icons or green buttons
                    has_play_icon = 'zmdi-play' in html or 'play' in classes.lower()
                    has_green_styling = 'green' in classes.lower() or 'green' in text
                    is_calculate_button = any(word in text for word in ['calculate', 'search', 'run', 'go'])
                    
                    if has_play_icon or (has_green_styling and is_calculate_button):
                        print(f"   🎯 Found potential green button: '{text}' (play: {has_play_icon}, green: {has_green_styling})")
                        
                        # Click it
                        await button.click()
                        print("   ✅ GREEN BUTTON CLICKED!")
                        
                        # Just wait a moment to confirm click registered
                        print("   ⏳ Button clicked, allowing calculation to start...")
                        await self.page.wait_for_timeout(2000)  # Brief wait
                        return True
                        
                except Exception as e:
                    print(f"   ⚠️ Error with button: {e}")
                    continue
            
            # Try original selectors as fallback
            for selector in play_button_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element and await element.is_visible():
                        print(f"   ✅ Found green play button: {selector}")
                        await element.click()
                        print("   ✅ GREEN PLAY BUTTON CLICKED!")
                        await self.page.wait_for_timeout(2000)  # Brief wait
                        return True
                except Exception as e:
                    continue
            
            print("   ⚠️ No green play button found - proceeding with existing results")
            return False
            
        except Exception as e:
            print(f"   ❌ Error finding green button: {e}")
            return False
    
    async def wait_for_all_lenders_to_load(self):
        """Wait for all lenders to populate in the results table."""
        try:
            print("   ⏰ Waiting minimum 60 seconds before checking lenders...")
            
            # Wait minimum 60 seconds first
            await self.page.wait_for_timeout(60000)  # 60 seconds mandatory wait
            
            print("   🔍 Progressive lender loading check (after 60s minimum wait)...")
            
            # Then check lender count over time to ensure all have loaded
            max_attempts = 4  # Reduced attempts since we already waited 60s (4 attempts × 7.5s = 30s additional)
            stable_count_needed = 3  # Need stability
            stable_count = 0
            last_lender_count = 0
            
            for attempt in range(max_attempts):
                # Get current page text to check for lenders
                page_text = await self.page.text_content('body')
                
                # Count known lender names in the page - also check for amounts
                # Use enhanced lender name variants for better detection
                lender_variants = [
                    "Gen H", "Generation Home", "Accord", "Skipton", "Kensington", "Precise", 
                    "Atom", "Atom Bank", "Clydesdale", "Newcastle", "Metro", "Metro Bank",
                    "Nottingham", "Nottingham Building Society", "Leeds", "Leeds Building Society", 
                    "Halifax", "HSBC", "Principality", "Coventry", "Santander", "Barclays", "Nationwide",
                    "Bank of Ireland", "BOI", "Hinckley & Rugby", "Hinckley & Rugby Building Society",
                    "Market Harborough", "Market Harborough Building Society"
                ]
                
                current_lender_count = sum(1 for lender in lender_variants if lender.lower() in page_text.lower())
                
                # Also check for pound signs to see if amounts are populated
                pound_count = page_text.count('£')
                
                print(f"   📊 Attempt {attempt + 1}: Found {current_lender_count} lenders, {pound_count} amounts")
                
                # Check if lender count has stabilized AND we have enough amounts
                if (current_lender_count == last_lender_count and 
                    current_lender_count >= 12 and 
                    pound_count >= 15):  # Need amounts populated too
                    stable_count += 1
                    if stable_count >= stable_count_needed:
                        print(f"   ✅ Lender count stable at {current_lender_count} with {pound_count} amounts - all loaded!")
                        return True
                else:
                    stable_count = 0  # Reset if count changed
                
                last_lender_count = current_lender_count
                
                # Wait before next check
                await self.page.wait_for_timeout(7500)  # Wait 7.5 seconds between checks (90s total: 12 * 7.5)
            
            print(f"   ⚠️ Finished waiting - final lender count: {last_lender_count}")
            return True  # Continue even if not all loaded
            
        except Exception as e:
            print(f"   ❌ Error waiting for lenders: {e}")
            return True  # Don't fail the whole process
    
    async def extract_real_lender_data(self):
        """Extract real lender data from affordability results table."""
        try:
            print("   📊 Looking for affordability results table with 'Lender', 'Affordable', 'Criteria' headers...")
            
            # Gradually scroll down to find the results table
            await self.gradual_scroll_to_find_table()
            
            # Look specifically for the affordability results table
            lenders_data = await self.find_affordability_table()
            
            if lenders_data:
                print(f"   ✅ Successfully extracted {len(lenders_data)} lender results from table:")
                for lender, amount in lenders_data.items():
                    if isinstance(amount, int):
                        print(f"      💰 {lender}: £{amount:,}")
                    else:
                        print(f"      📋 {lender}: {amount}")
                return lenders_data
            else:
                print("   ⚠️ No affordability table found - trying fallback extraction...")
                return await self.fallback_lender_extraction()
                
        except Exception as e:
            print(f"   ❌ Error extracting lender data: {e}")
            return {}
    
    async def gradual_scroll_to_find_table(self):
        """Gradually scroll down to find the affordability results table."""
        try:
            print("   🔍 Scrolling to find affordability table...")
            
            # Simple scroll to position where table usually appears
            await self.page.evaluate("window.scrollTo(0, 500)")
            await self.page.wait_for_timeout(2000)
            
            # Check if we can see table headers
            page_text = await self.page.text_content('body')
            if 'affordable' in page_text.lower() and 'lender' in page_text.lower():
                print("   ✅ Found affordability table indicators")
            else:
                print("   🔄 Table not visible, scrolling more...")
                # Scroll down more
                await self.page.evaluate("window.scrollTo(0, 1500)")
                await self.page.wait_for_timeout(2000)
            
            # Take screenshot for debugging
            await self.page.screenshot(path="table_search_position.png")
            
        except Exception as e:
            print(f"   ⚠️ Error during scroll: {e}")
    
    async def find_affordability_table(self):
        """Find and extract data from the specific affordability results table."""
        try:
            print("   🔍 Looking for affordability table...")
            
            # Enhanced lender matching with full names and alternatives
            target_lenders = {
                "Gen H": ["Gen H", "Generation Home", "GenerationHome", "genH"],
                "Accord": ["Accord"],
                "Skipton": ["Skipton"],
                "Kensington": ["Kensington"],
                "Precise": ["Precise"],
                "Atom": ["Atom", "Atom Bank", "AtomBank", "Atom bank"],
                "Clydesdale": ["Clydesdale"],
                "Newcastle": ["Newcastle"],
                "Metro": ["Metro", "Metro Bank", "MetroBank", "Metro bank"],
                "Nottingham": ["Nottingham", "Nottingham Building Society", "Nottingham BS"],
                "Leeds": ["Leeds", "Leeds Building Society", "Leeds BS"],
                "Halifax": ["Halifax"],
                "Santander": ["Santander"],
                "Barclays": ["Barclays"],
                "HSBC": ["HSBC"],
                "Nationwide": ["Nationwide"],
                "Coventry": ["Coventry"],
                "Principality": ["Principality"],
                "Furness": ["Furness"],
                "Penrith": ["Penrith"],
                "Bank of Ireland": ["Bank of Ireland", "BOI"],
                "Hinckley & Rugby": ["Hinckley & Rugby", "Hinckley & Rugby Building Society", "Hinckley Rugby", "H&R BS"],
                "Market Harborough": ["Market Harborough", "Market Harborough Building Society", "MH BS", "MHBS"]
            }
            
            # Look for tables on the page
            tables = await self.page.query_selector_all('table')
            print(f"   📊 Found {len(tables)} tables on page")
            
            for table_idx, table in enumerate(tables):
                try:
                    table_text = await table.text_content()
                    
                    # Check if this table contains affordability data
                    if ('lender' in table_text.lower() and 'affordable' in table_text.lower()):
                        print(f"   🎯 Found affordability table {table_idx + 1}")
                        
                        # Extract using the proven method
                        return await self.extract_from_affordability_table(table, target_lenders)
                                
                except Exception as e:
                    print(f"   ⚠️ Error processing table {table_idx + 1}: {e}")
                    continue
            
            print("   ⚠️ No affordability table found")
            return {}
            
        except Exception as e:
            print(f"   ⚠️ Error finding affordability table: {e}")
            return {}
    
    async def extract_from_affordability_table(self, table, target_lenders):
        """Extract target lenders from the affordability table using proven method."""
        try:
            print("   📊 Extracting target lenders from table...")
            
            results = {}
            
            # Get all rows
            rows = await table.query_selector_all('tr')
            print(f"   📋 Processing {len(rows)} rows...")
            
            # Process all data rows (skip header row)
            for row_idx, row in enumerate(rows[1:], 1):
                try:
                    cells = await row.query_selector_all('td, th')
                    
                    if len(cells) >= 3:  # Need at least lender, affordable, criteria columns
                        # Get lender name (column 1) and affordable amount (column 2)
                        lender_cell = cells[1]
                        lender_text = await lender_cell.text_content()
                        lender_name = lender_text.strip()
                        
                        affordable_cell = cells[2]
                        affordable_text = await affordable_cell.text_content()
                        
                        # Check if this is one of our target lenders using enhanced matching
                        for standard_name, name_variants in target_lenders.items():
                            lender_found = False
                            for variant in name_variants:
                                if variant.lower() in lender_name.lower():
                                    # Extract amount - handle ranges by taking the higher value
                                    import re
                                    
                                    # Check for ranges like "£75,000 to £100,000"
                                    range_match = re.search(r'£?([\d,]+)\s+to\s+£?([\d,]+)', affordable_text)
                                    if range_match:
                                        # Take the higher number from the range
                                        lower_amount = int(range_match.group(1).replace(',', ''))
                                        higher_amount = int(range_match.group(2).replace(',', ''))
                                        amount = higher_amount
                                        print(f"   📊 Found range: £{lower_amount:,} to £{higher_amount:,} - using higher value")
                                    else:
                                        # Single amount
                                        amounts = re.findall(r'£?([\d,]+)', affordable_text)
                                        if amounts:
                                            amount_str = amounts[0].replace(',', '')
                                            amount = int(amount_str)
                                        else:
                                            continue
                                    
                                    # Validate amount is reasonable
                                    if 10000 <= amount <= 2000000:
                                        results[standard_name] = amount
                                        print(f"   💰 {standard_name}: £{amount:,} (matched: '{variant}' in '{lender_name}')")
                                        lender_found = True
                                        break  # Found this target lender, move to next row
                                        
                            if lender_found:
                                break
                        
                except Exception as e:
                    continue
            
            print(f"   ✅ Successfully extracted {len(results)} target lenders")
            return results
            
        except Exception as e:
            print(f"   ❌ Error extracting from table: {e}")
            return {}
    
    async def fallback_lender_extraction(self):
        """Fallback method to extract lender data if table method fails."""
        try:
            print("   🔍 Fallback: Looking for lender data in page elements...")
            
            lenders_data = {}
            # Use same enhanced lender matching
            target_lenders = {
                "Gen H": ["Gen H", "Generation Home", "GenerationHome", "genH"],
                "Accord": ["Accord"],
                "Skipton": ["Skipton"],
                "Kensington": ["Kensington"],
                "Precise": ["Precise"],
                "Atom": ["Atom", "Atom Bank", "AtomBank", "Atom bank"],
                "Clydesdale": ["Clydesdale"],
                "Newcastle": ["Newcastle"],
                "Metro": ["Metro", "Metro Bank", "MetroBank", "Metro bank"],
                "Nottingham": ["Nottingham", "Nottingham Building Society", "Nottingham BS"],
                "Leeds": ["Leeds", "Leeds Building Society", "Leeds BS"],
                "Halifax": ["Halifax"],
                "Santander": ["Santander"],
                "Barclays": ["Barclays"],
                "HSBC": ["HSBC"],
                "Nationwide": ["Nationwide"],
                "Coventry": ["Coventry"],
                "Principality": ["Principality"],
                "Furness": ["Furness"],
                "Penrith": ["Penrith"],
                "Bank of Ireland": ["Bank of Ireland", "BOI"],
                "Hinckley & Rugby": ["Hinckley & Rugby", "Hinckley & Rugby Building Society", "Hinckley Rugby", "H&R BS"],
                "Market Harborough": ["Market Harborough", "Market Harborough Building Society", "MH BS", "MHBS"]
            }
            
            # Get all text content and look for patterns
            page_text = await self.page.text_content('body')
            lines = page_text.split('\n')
            
            # Look for lines containing lender names and amounts
            for line in lines:
                line = line.strip()
                if not line or len(line) < 10:
                    continue
                    
                for standard_name, name_variants in target_lenders.items():
                    if standard_name in lenders_data:
                        continue  # Already found this lender
                        
                    for variant in name_variants:
                        if variant.lower() in line.lower() and '£' in line:
                            import re
                            amounts = re.findall(r'£([\d,]+)', line)
                            if amounts:
                                try:
                                    amount = int(amounts[0].replace(',', ''))
                                    if 10000 <= amount <= 10000000:
                                        lenders_data[standard_name] = amount
                                        print(f"   💰 {standard_name}: £{amount:,} (fallback, matched: '{variant}')")
                                        break
                                except ValueError:
                                    continue
                        if standard_name in lenders_data:
                            break
            
            return lenders_data
            
        except Exception as e:
            print(f"   ⚠️ Fallback extraction error: {e}")
            return {}

# Test function to run a single scenario
async def test_real_automation():
    """Test the real automation with one scenario."""
    automation = RealMBTAutomation()
    
    try:
        await automation.start_browser()
        
        # Login
        login_success = await automation.login()
        if not login_success:
            print("❌ Login failed")
            return
        
        # Run one test scenario with different income to verify fresh calculation
        result = await automation.run_single_scenario("E.Single", 35000)
        
        if result:
            print(f"\\n🎉 SUCCESS!")
            print(f"📊 Result: {result}")
            
            # Save result
            with open("real_automation_test.json", "w") as f:
                json.dump(result, f, indent=2)
            print("💾 Result saved to real_automation_test.json")
        else:
            print("❌ No result obtained")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        await automation.close()

if __name__ == "__main__":
    asyncio.run(test_real_automation())