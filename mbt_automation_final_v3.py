"""
Final MBT automation v3 - Based on actual form structure observed.
Fill ALL required fields section by section to unlock subsequent sections.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv
import re

load_dotenv()

class MBTAutomationFinalV3:
    """MBT automation that properly handles the progressive form structure."""
    
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
            args=['--no-sandbox', '--disable-dev-shm-usage'],
            slow_mo=500 if not headless else 0
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
            
            # Return to dashboard
            await self.page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await self.page.wait_for_load_state("networkidle")
            await self.page.wait_for_timeout(2000)
            
            # Create new case
            await self.page.click('text=Create RESI Case')
            await self.page.wait_for_load_state("networkidle")
            await self.page.wait_for_timeout(3000)
            
            print(f"✅ New case created: {self.page.url}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating case: {e}")
            return False
    
    async def fill_all_visible_required_fields(self, scenario: Dict) -> bool:
        """Fill ALL visible required fields (red asterisks) to unlock next sections."""
        try:
            print("📋 Filling ALL visible required fields...")
            
            # SECTION 1: Basic applicant details
            print("👤 Section 1: Basic applicant details")
            basic_fields = [
                ('input[name="firstname"]', 'Test'),
                ('input[name="surname"]', 'User'),
                ('input[name="email"]', f'test-{scenario["scenario_id"]}@example.com')
            ]
            
            for selector, value in basic_fields:
                try:
                    field = await self.page.query_selector(selector)
                    if field and await field.is_visible():
                        await field.fill(value)
                        print(f"✅ Filled {selector}")
                except:
                    pass
            
            # SECTION 2: Property and mortgage details  
            print("🏡 Section 2: Property and mortgage details")
            
            # Property value (already filled from screenshot)
            purchase_field = await self.page.query_selector('input[name="purchase"]')
            if purchase_field:
                await purchase_field.fill('1000000')
                print("✅ Property value: £1,000,000")
            
            # Loan amount (already filled from screenshot)
            loan_field = await self.page.query_selector('input[name="loan_amount"]')
            if loan_field:
                await loan_field.fill('100000')
                print("✅ Loan amount: £100,000")
            
            # CRITICAL: Fill the required dropdowns visible in screenshot
            
            # Region dropdown (red asterisk visible)
            print("🌍 Setting Region...")
            region_select = await self.page.query_selector('select[name*="region"], select:has-text(\"Region\")')
            if region_select:
                try:
                    await region_select.select_option('England')
                    print("✅ Region set to England")
                except:
                    try:
                        await region_select.select_option(index=1)  # Select first real option
                        print("✅ Region set (first option)")
                    except:
                        pass
            
            # Ownership dropdown (red asterisk visible) 
            print("🏠 Setting Ownership...")
            ownership_select = await self.page.query_selector('select[name*="ownership"]')
            if ownership_select:
                try:
                    await ownership_select.select_option('Freehold')
                    print("✅ Ownership set to Freehold")
                except:
                    try:
                        await ownership_select.select_option(index=1)
                        print("✅ Ownership set (first option)")
                    except:
                        pass
            
            # Fill all other required fields comprehensively
            await self.fill_all_required_fields_on_page()
            
            # CRITICAL: Scroll down to see if there are more sections
            print("📜 Scrolling to reveal more sections...")
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(2000)
            
            # Take screenshot after filling required fields
            await self.page.screenshot(path=f"after_required_fields_{scenario['scenario_id']}.png")
            print("📸 Screenshot saved after filling required fields")
            
            return True
            
        except Exception as e:
            print(f"❌ Error filling required fields: {e}")
            return False
    
    async def dismiss_modal_dialogs(self) -> bool:
        """Dismiss any modal dialogs that appear."""
        try:
            print("🔔 Checking for modal dialogs...")
            
            # Wait a moment for modals to appear
            await self.page.wait_for_timeout(1000)
            
            # Look for modal dialogs and close buttons with more comprehensive selectors
            modal_selectors = [
                'button:has-text("OK")',
                'button:has-text("Close")', 
                'button[class*="close"]',
                '.modal button',
                '[role="dialog"] button',
                '.modal-footer button',
                '.alert button',
                'button[ng-click*="close"]',
                'button[ng-click*="dismiss"]'
            ]
            
            dismissed = False
            for selector in modal_selectors:
                try:
                    modal_buttons = await self.page.query_selector_all(selector)
                    for button in modal_buttons:
                        if await button.is_visible():
                            await button.click()
                            print(f"✅ Dismissed modal using {selector}")
                            await self.page.wait_for_timeout(1000)
                            dismissed = True
                            break
                    if dismissed:
                        break
                except Exception as e:
                    print(f"⚠️ Error with selector {selector}: {e}")
                    continue
            
            # Try clicking outside modal area to dismiss
            if not dismissed:
                try:
                    # Check if modal backdrop exists and click it
                    backdrop = await self.page.query_selector('.modal-backdrop, .modal-overlay')
                    if backdrop:
                        await backdrop.click()
                        print("✅ Clicked modal backdrop to dismiss")
                        await self.page.wait_for_timeout(1000)
                        dismissed = True
                except:
                    pass
            
            # Try pressing Escape key
            if not dismissed:
                try:
                    await self.page.keyboard.press('Escape')
                    print("✅ Pressed Escape to dismiss dialogs")
                    await self.page.wait_for_timeout(1000)
                    dismissed = True
                except:
                    pass
            
            # Force dismiss by clicking on page background if modal still exists
            if not dismissed:
                try:
                    # Click on the main content area to force focus away from modal
                    await self.page.click('body', position={'x': 100, 'y': 100})
                    print("✅ Clicked background to dismiss modal")
                    await self.page.wait_for_timeout(1000)
                except:
                    pass
            
            return True
            
        except Exception as e:
            print(f"❌ Error dismissing modals: {e}")
            return False
    
    async def fill_specific_dropdowns_robustly(self) -> bool:
        """Fill the specific dropdowns that are causing validation errors."""
        try:
            print("🎯 Filling specific required dropdowns robustly...")
            
            # Get all select elements and analyze them
            all_selects = await self.page.query_selector_all('select')
            print(f"Found {len(all_selects)} select elements")
            
            for i, select in enumerate(all_selects):
                try:
                    # Get select attributes
                    name = await select.get_attribute('name') or ''
                    id_attr = await select.get_attribute('id') or ''
                    is_visible = await select.is_visible()
                    
                    if not is_visible:
                        continue
                        
                    print(f"  Select {i+1}: name='{name}', id='{id_attr}'")
                    
                    # Get all options for this select
                    options = await select.query_selector_all('option')
                    option_texts = []
                    for option in options:
                        text = await option.text_content()
                        value = await option.get_attribute('value')
                        option_texts.append(f"'{text}' (value: {value})")
                    
                    print(f"    Options: {option_texts}")
                    
                    # Determine what this dropdown is for and set appropriate value
                    if any(keyword in name.lower() for keyword in ['reason', 'mortgage']):
                        print(f"🎯 This is the Reason for Mortgage dropdown")
                        # Try common mortgage reasons
                        for reason in ['Purchase', 'purchase', 'Buy', 'buy', 'Buying']:
                            try:
                                await select.select_option(reason)
                                print(f"✅ Set Reason for Mortgage to: {reason}")
                                await self.page.wait_for_timeout(1000)
                                break
                            except:
                                continue
                        else:
                            # If no specific option works, select first non-empty option
                            if len(options) > 1:
                                try:
                                    await select.select_option(index=1)
                                    print("✅ Set Reason for Mortgage (first option)")
                                except:
                                    pass
                    
                    elif any(keyword in name.lower() for keyword in ['property', 'type']):
                        print(f"🎯 This is the Property Type dropdown")
                        # Try common property types
                        for prop_type in ['House', 'house', 'Detached', 'detached', 'Semi', 'semi']:
                            try:
                                await select.select_option(prop_type)
                                print(f"✅ Set Property Type to: {prop_type}")
                                await self.page.wait_for_timeout(1000)
                                break
                            except:
                                continue
                        else:
                            # If no specific option works, select first non-empty option
                            if len(options) > 1:
                                try:
                                    await select.select_option(index=1)
                                    print("✅ Set Property Type (first option)")
                                except:
                                    pass
                    
                    elif any(keyword in name.lower() for keyword in ['term', 'year']):
                        print(f"🎯 This might be a term dropdown")
                        # Try to set 35 years or similar
                        for term in ['35', '30', '25']:
                            try:
                                await select.select_option(term)
                                print(f"✅ Set Term to: {term} years")
                                await self.page.wait_for_timeout(1000)
                                break
                            except:
                                continue
                    
                    # Small delay between dropdowns
                    await self.page.wait_for_timeout(500)
                    
                except Exception as e:
                    print(f"⚠️ Error with select {i+1}: {e}")
                    continue
            
            print("✅ Dropdown filling completed")
            return True
            
        except Exception as e:
            print(f"❌ Error filling dropdowns: {e}")
            return False
    
    async def fill_all_required_fields_on_page(self) -> bool:
        """Fill ALL required fields that might be visible on the current page."""
        try:
            print("📝 Filling all required fields comprehensively...")
            
            # MORTGAGE PREFERENCES - Enhanced dropdown handling
            await self.fill_specific_dropdowns_robustly()
            
            # Tenure radio buttons (Freehold)
            print("🏛️ Setting Tenure to Freehold...")
            freehold_radio = await self.page.query_selector('input[type="radio"][value*="Freehold"], input[type="radio"][value*="freehold"]')
            if freehold_radio:
                try:
                    await freehold_radio.check()
                    print("✅ Tenure set to Freehold")
                except:
                    pass
            
            # PROPERTY DETAILS
            # Main residence (Yes)
            main_residence_yes = await self.page.query_selector('input[name*="main_residence"][value="Yes"]')
            if main_residence_yes:
                await main_residence_yes.check()
                print("✅ Main residence: Yes")
            
            # Debt consolidation (No)
            debt_consolidation_no = await self.page.query_selector('input[name*="debt_consolidation"][value="No"]')
            if debt_consolidation_no:
                await debt_consolidation_no.check()
                print("✅ Debt consolidation: No")
            
            # Green mortgage (No)
            green_mortgage_no = await self.page.query_selector('input[name*="green"][value="No"]')
            if green_mortgage_no:
                await green_mortgage_no.check()
                print("✅ Green mortgage: No")
            
            # New build (No)
            new_build_no = await self.page.query_selector('input[name*="new_build"][value="No"], input[value="No"]')
            if new_build_no:
                try:
                    page_text = await self.page.text_content('body')
                    if 'new build' in page_text.lower():
                        await new_build_no.check()
                        print("✅ New build: No")
                except:
                    pass
            
            # Mortgage product term checkbox (if visible)
            print("⏱️ Setting mortgage term...")
            term_checkboxes = await self.page.query_selector_all('input[type="checkbox"]')
            for checkbox in term_checkboxes:
                try:
                    name = await checkbox.get_attribute('name')
                    if name and 'term' in name.lower():
                        # Check if it's likely the right term (we want 35 years or similar)
                        parent_text = await checkbox.text_content()
                        if not parent_text:
                            parent = await checkbox.query_selector('..')
                            if parent:
                                parent_text = await parent.text_content()
                        
                        if parent_text and any(term in parent_text for term in ['35', '30', '25']):
                            await checkbox.check()
                            print(f"✅ Checked mortgage term checkbox")
                            break
                except:
                    continue
            
            print("✅ Required fields completion attempted")
            return True
            
        except Exception as e:
            print(f"❌ Error filling required fields: {e}")
            return False
    
    async def find_and_fill_applicant_section(self, scenario: Dict) -> bool:
        """Find and fill the applicant section that should now be visible."""
        try:
            print("👥 Looking for applicant section...")
            
            # CRITICAL: Check for "Joint application?" checkbox first
            print("🔍 Looking for Joint application checkbox...")
            joint_checkbox = await self.page.query_selector('input[type="checkbox"]')
            if joint_checkbox and scenario['applicant_type'] == 'joint':
                try:
                    # Check if it's the joint application checkbox
                    checkbox_text = await self.page.text_content('body')
                    if 'joint application' in checkbox_text.lower():
                        await joint_checkbox.check()
                        print("✅ Checked 'Joint application?' checkbox")
                        await self.page.wait_for_timeout(3000)  # Wait for form to update
                        
                        # Take screenshot after checking joint application
                        await self.page.screenshot(path=f"after_joint_checkbox_{scenario['scenario_id']}.png")
                        print("📸 Screenshot after joint checkbox")
                except Exception as e:
                    print(f"⚠️ Could not check joint checkbox: {e}")
            
            # Fill any remaining required fields before submitting
            await self.fill_all_required_fields_on_page()
            
            # Multiple attempts to progress through validation
            max_attempts = 3
            for attempt in range(max_attempts):
                print(f"🚀 Attempt {attempt + 1}/{max_attempts}: Submitting to progress...")
                
                # Dismiss any modal dialogs first
                await self.dismiss_modal_dialogs()
                
                # Try to submit current section to progress to applicant details
                submit_button = await self.page.query_selector('button[type="submit"], input[type="submit"]')
                if submit_button:
                    await submit_button.click()
                    await self.page.wait_for_timeout(3000)
                    
                    # Handle any modal dialogs that appear after submit
                    await self.dismiss_modal_dialogs()
                    
                    # Wait for any page changes
                    await self.page.wait_for_load_state("networkidle", timeout=10000)
                    
                    # Check if we progressed (URL change or new sections visible)
                    current_url = self.page.url
                    print(f"Current URL: {current_url}")
                    
                    # Check if validation errors are gone by looking for applicant fields
                    applicant_fields = await self.page.query_selector_all('select, input[name*="employment"], input[name*="income"]')
                    if len(applicant_fields) > 0:
                        print(f"✅ Progress detected - found {len(applicant_fields)} potential applicant fields")
                        break
                    
                    # If still getting validation errors, fill dropdowns again
                    page_text = await self.page.text_content('body')
                    if 'please' in page_text.lower() and ('choose' in page_text.lower() or 'select' in page_text.lower()):
                        print("⚠️ Still getting validation errors, re-filling dropdowns...")
                        await self.fill_all_required_fields_on_page()
                    else:
                        print("✅ No obvious validation errors, progressing...")
                        break
                else:
                    print("❌ No submit button found")
                    break
                    
                await self.page.wait_for_timeout(2000)
            
            # Take screenshot to see current state
            await self.page.screenshot(path=f"after_submit_{scenario['scenario_id']}.png")
            print("📸 Screenshot after submit attempts")
            
            # Now look for applicant-related dropdowns/fields
            print("🔍 Looking for applicant count and employment fields...")
            
            # Look for ALL select elements
            all_selects = await self.page.query_selector_all('select')
            print(f"Found {len(all_selects)} select elements")
            
            for i, select in enumerate(all_selects):
                try:
                    name = await select.get_attribute('name')
                    if name:
                        print(f"  Select {i+1}: name='{name}'")
                        
                        # If this looks like applicant count
                        if any(keyword in name.lower() for keyword in ['applicant', 'number']):
                            print(f"🎯 Found applicant count field: {name}")
                            
                            # Set number of applicants
                            applicant_count = 2 if scenario['applicant_type'] == 'joint' else 1
                            try:
                                await select.select_option(str(applicant_count))
                                print(f"✅ Set {applicant_count} applicant(s)")
                                await self.page.wait_for_timeout(2000)  # Wait for form update
                            except Exception as e:
                                print(f"❌ Could not set applicant count: {e}")
                        
                        # If this looks like employment
                        elif any(keyword in name.lower() for keyword in ['employment', 'status']):
                            print(f"🎯 Found employment field: {name}")
                            
                            # Set employment status
                            if scenario['applicant1_employment'] == 'employed':
                                employment_value = 'Employed'
                            else:
                                employment_value = 'Self Employed (Sole Trader)'
                            
                            try:
                                await select.select_option(employment_value)
                                print(f"✅ Set employment to: {employment_value}")
                                await self.page.wait_for_timeout(3000)  # Wait for income fields
                            except:
                                try:
                                    # Try simpler values
                                    if 'employed' in employment_value.lower():
                                        await select.select_option('Employed')
                                    else:
                                        await select.select_option('Self Employed')
                                    print(f"✅ Set employment (alternative)")
                                except Exception as e:
                                    print(f"❌ Could not set employment: {e}")
                except:
                    continue
            
            return True
            
        except Exception as e:
            print(f"❌ Error in applicant section: {e}")
            return False
    
    async def find_and_fill_income_fields(self, scenario: Dict) -> bool:
        """Find and fill income fields that should now be visible."""
        try:
            print("💰 Looking for income fields...")
            
            income_amount = scenario['applicant1_income']
            
            # Look for ALL input fields again
            all_inputs = await self.page.query_selector_all('input')
            income_fields = []
            
            for input_field in all_inputs:
                try:
                    name = await input_field.get_attribute('name')
                    if name and any(keyword in name.lower() for keyword in ['income', 'salary', 'basic', 'net_profit']):
                        is_visible = await input_field.is_visible()
                        if is_visible:
                            income_fields.append({
                                'element': input_field,
                                'name': name
                            })
                except:
                    continue
            
            print(f"Found {len(income_fields)} VISIBLE income fields:")
            for field in income_fields:
                print(f"   ✅ {field['name']}")
            
            # Fill income fields based on employment type
            filled_count = 0
            
            if scenario['applicant1_employment'] == 'employed':
                # For employed - fill basic income fields
                for field in income_fields:
                    if any(keyword in field['name'].lower() for keyword in ['income_amount', 'basic_salary', 'salary']):
                        try:
                            await field['element'].fill(str(income_amount))
                            print(f"✅ Filled {field['name']} with £{income_amount:,}")
                            filled_count += 1
                        except Exception as e:
                            print(f"❌ Could not fill {field['name']}: {e}")
            
            else:
                # For self-employed - fill net profit fields with pattern
                year1_amount = income_amount
                year2_amount = income_amount // 2
                year3_amount = 0
                
                for field in income_fields:
                    name = field['name'].lower()
                    try:
                        if 'year_1' in name or 'last' in name:
                            await field['element'].fill(str(year1_amount))
                            print(f"✅ Filled {field['name']} (Year 1) with £{year1_amount:,}")
                            filled_count += 1
                        elif 'year_2' in name:
                            await field['element'].fill(str(year2_amount))
                            print(f"✅ Filled {field['name']} (Year 2) with £{year2_amount:,}")
                            filled_count += 1
                        elif 'year_3' in name:
                            await field['element'].fill(str(year3_amount))
                            print(f"✅ Filled {field['name']} (Year 3) with £{year3_amount:,}")
                            filled_count += 1
                        elif 'net_profit' in name and not any(year in name for year in ['year_1', 'year_2', 'year_3']):
                            # Generic net profit field
                            await field['element'].fill(str(year1_amount))
                            print(f"✅ Filled {field['name']} with £{year1_amount:,}")
                            filled_count += 1
                    except Exception as e:
                        print(f"❌ Could not fill {field['name']}: {e}")
                
                # Set time in business for self-employed
                await self.set_time_in_business()
            
            print(f"📊 Successfully filled {filled_count} income fields")
            return filled_count > 0
            
        except Exception as e:
            print(f"❌ Error filling income: {e}")
            return False
    
    async def set_time_in_business(self) -> bool:
        """Set time in business to 2 years 0 months."""
        try:
            print("📅 Setting time in business: 2 years 0 months")
            
            # Look for business time dropdowns
            all_selects = await self.page.query_selector_all('select')
            
            for select in all_selects:
                name = await select.get_attribute('name')
                if name and 'business' in name.lower():
                    if 'year' in name.lower():
                        try:
                            await select.select_option('2')
                            print("✅ Business years: 2")
                        except:
                            pass
                    elif 'month' in name.lower():
                        try:
                            await select.select_option('0')
                            print("✅ Business months: 0")
                        except:
                            pass
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting time in business: {e}")
            return False
    
    async def submit_and_extract_results(self, scenario: Dict) -> Dict[str, float]:
        """Submit form and extract results."""
        try:
            print("🚀 Final submit and results extraction...")
            
            # Take screenshot before final submit
            await self.page.screenshot(path=f"before_final_submit_{scenario['scenario_id']}.png")
            
            # Submit the form
            submit_button = await self.page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                print("📤 Final form submitted")
                
                # Wait for results
                await self.page.wait_for_timeout(15000)  # Longer wait for processing
                await self.page.wait_for_load_state("networkidle", timeout=60000)
                
                # Take screenshot of results
                await self.page.screenshot(path=f"final_results_{scenario['scenario_id']}.png")
                print(f"📸 Results screenshot saved")
                
                # Extract results
                results = await self.extract_lender_results()
                return results
            else:
                print("❌ No final submit button found")
                return {}
                
        except Exception as e:
            print(f"❌ Error in final submit: {e}")
            return {}
    
    async def extract_lender_results(self) -> Dict[str, float]:
        """Extract lender results from the page."""
        try:
            print("📊 Extracting lender results...")
            results = {}
            
            # Get page content
            page_text = await self.page.text_content('body')
            
            # Look for lender results in various formats
            for lender in self.target_lenders:
                # Pattern to find lender name followed by amount
                patterns = [
                    rf'{re.escape(lender)}.*?£([\d,]+)',
                    rf'{re.escape(lender)}.*?([\d,]+)',
                    rf'{lender}.*?£([\d,]+)',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE | re.DOTALL)
                    if matches:
                        # Convert to numbers and take the largest
                        amounts = []
                        for match in matches:
                            try:
                                amount = float(str(match).replace(',', '').replace('£', ''))
                                if amount > 1000:  # Reasonable minimum
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
    
    async def run_scenario(self, scenario: Dict) -> Dict[str, float]:
        """Run complete scenario with progressive form handling."""
        try:
            print(f"\n🎯 === RUNNING SCENARIO: {scenario['scenario_id']} ===")
            print(f"Type: {scenario['applicant_type']}")
            print(f"Income: £{scenario['applicant1_income']:,}")
            print(f"Employment: {scenario['applicant1_employment']}")
            
            # Progressive workflow
            steps = [
                ("Create new case", lambda: self.create_new_case(scenario)),
                ("Fill all required fields", lambda: self.fill_all_visible_required_fields(scenario)),
                ("Find applicant section", lambda: self.find_and_fill_applicant_section(scenario)),
                ("Fill income fields", lambda: self.find_and_fill_income_fields(scenario)),
                ("Submit and extract", lambda: self.submit_and_extract_results(scenario))
            ]
            
            for step_name, step_func in steps:
                print(f"\n--- {step_name.upper()} ---")
                result = await step_func()
                
                if step_name == "Submit and extract":
                    return result if result else {}
                elif not result:
                    print(f"❌ Step '{step_name}' failed")
                    # Continue anyway for debugging
                
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
async def test_final_v3():
    """Test the final v3 automation."""
    mbt = MBTAutomationFinalV3()
    
    try:
        await mbt.start_browser(headless=False)
        
        if not await mbt.login():
            print("Login failed")
            return
        
        # Test one scenario first
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
            print(f"\n📊 SUCCESS - Results for {test_scenario['scenario_id']}:")
            for lender, amount in results.items():
                print(f"   {lender}: £{amount:,.0f}")
        else:
            print(f"\n❌ No results obtained for {test_scenario['scenario_id']}")
    
    finally:
        print("\n⏳ Keeping browser open for inspection...")
        await asyncio.sleep(60)
        await mbt.close()


if __name__ == "__main__":
    asyncio.run(test_final_v3())