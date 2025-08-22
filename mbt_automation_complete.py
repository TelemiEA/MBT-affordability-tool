"""
Complete MBT automation based on all our testing and debugging.
This version handles the full workflow from login to results extraction.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv
import re

load_dotenv()

class MBTAutomationComplete:
    """Complete MBT automation with all lessons learned integrated."""
    
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
            
            # Try multiple methods to dismiss modals
            modal_selectors = [
                'button:has-text("OK")',
                'button:has-text("Close")',
                '[role="dialog"] button',
                '.modal button'
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
            
            # Try escape key
            try:
                await self.page.keyboard.press('Escape')
                await self.page.wait_for_timeout(1000)
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Error dismissing modals: {e}")
            return False
    
    async def fill_comprehensive_form(self, scenario: Dict) -> bool:
        """Fill all form sections comprehensively."""
        try:
            print("📋 Filling comprehensive form...")
            
            # SECTION 1: Basic details
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
            
            # SECTION 2: ALL dropdowns with intelligent selection
            await self.fill_all_dropdowns_intelligently()
            
            # SECTION 3: Radio buttons and checkboxes
            await self.set_radio_buttons_and_checkboxes(scenario)
            
            # SECTION 4: Joint application if needed
            if scenario['applicant_type'] == 'joint':
                joint_checkbox = await self.page.query_selector('input[type="checkbox"]')
                if joint_checkbox:
                    try:
                        await joint_checkbox.check()
                        print("✅ Checked joint application")
                        await self.page.wait_for_timeout(2000)
                    except:
                        pass
            
            return True
            
        except Exception as e:
            print(f"❌ Error filling form: {e}")
            return False
    
    async def fill_all_dropdowns_intelligently(self) -> bool:
        """Fill ALL dropdowns with intelligent option selection."""
        try:
            all_selects = await self.page.query_selector_all('select')
            print(f"Found {len(all_selects)} dropdowns to fill")
            
            for i, select in enumerate(all_selects):
                try:
                    if not await select.is_visible():
                        continue
                    
                    name = await select.get_attribute('name') or ''
                    
                    # Get options
                    options = await select.query_selector_all('option')
                    if len(options) <= 1:
                        continue
                    
                    option_texts = []
                    for option in options:
                        text = await option.text_content()
                        option_texts.append(text)
                    
                    print(f"  Dropdown {i+1} (name: {name}): {option_texts}")
                    
                    # Intelligent selection based on dropdown purpose
                    selected = False
                    
                    # Mortgage reason
                    if any(keyword in name.lower() for keyword in ['reason', 'purpose']):
                        for reason in ['Purchase', 'purchase', 'Buy', 'buy']:
                            try:
                                await select.select_option(reason)
                                print(f"✅ Set mortgage reason to: {reason}")
                                selected = True
                                break
                            except:
                                continue
                    
                    # Property type
                    elif any(keyword in name.lower() for keyword in ['property', 'type']):
                        for prop_type in ['House', 'house', 'Detached', 'detached']:
                            try:
                                await select.select_option(prop_type)
                                print(f"✅ Set property type to: {prop_type}")
                                selected = True
                                break
                            except:
                                continue
                    
                    # Region
                    elif 'region' in name.lower():
                        for region in ['England', 'england', 'UK', 'United Kingdom']:
                            try:
                                await select.select_option(region)
                                print(f"✅ Set region to: {region}")
                                selected = True
                                break
                            except:
                                continue
                    
                    # Ownership/Tenure
                    elif any(keyword in name.lower() for keyword in ['ownership', 'tenure']):
                        for ownership in ['Freehold', 'freehold', 'Owner']:
                            try:
                                await select.select_option(ownership)
                                print(f"✅ Set ownership to: {ownership}")
                                selected = True
                                break
                            except:
                                continue
                    
                    # Term
                    elif 'term' in name.lower():
                        for term in ['35', '30', '25']:
                            try:
                                await select.select_option(term)
                                print(f"✅ Set term to: {term}")
                                selected = True
                                break
                            except:
                                continue
                    
                    # Employment status
                    elif any(keyword in name.lower() for keyword in ['employment', 'status']):
                        if scenario['applicant1_employment'] == 'employed':
                            employment_value = 'Employed'
                        else:
                            employment_value = 'Self Employed'
                        
                        try:
                            await select.select_option(employment_value)
                            print(f"✅ Set employment to: {employment_value}")
                            selected = True
                        except:
                            pass
                    
                    # If no specific match, select first non-empty option
                    if not selected and len(options) > 1:
                        try:
                            await select.select_option(index=1)
                            print(f"✅ Set dropdown {i+1} to first option")
                        except:
                            pass
                    
                    await self.page.wait_for_timeout(500)
                    
                except Exception as e:
                    print(f"⚠️ Error with dropdown {i+1}: {e}")
                    continue
            
            return True
            
        except Exception as e:
            print(f"❌ Error filling dropdowns: {e}")
            return False
    
    async def set_radio_buttons_and_checkboxes(self, scenario: Dict) -> bool:
        """Set appropriate radio buttons and checkboxes."""
        try:
            # Common radio button selections
            radio_selections = [
                ('input[type="radio"][value="Yes"]', 'main residence'),
                ('input[type="radio"][value="No"]', 'debt consolidation'),
                ('input[type="radio"][value="No"]', 'green mortgage'),
                ('input[type="radio"][value="Freehold"]', 'tenure'),
                ('input[type="radio"][value="No"]', 'new build'),
                ('input[type="radio"][value="No"]', 'later life lending')
            ]
            
            for selector, context in radio_selections:
                try:
                    radio = await self.page.query_selector(selector)
                    if radio and await radio.is_visible():
                        await radio.check()
                        print(f"✅ Set {context} radio button")
                except:
                    pass
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting radio buttons: {e}")
            return False
    
    async def progress_through_sections(self, scenario: Dict, max_sections: int = 5) -> bool:
        """Progress through multiple form sections until reaching applicant details."""
        try:
            for section in range(max_sections):
                print(f"\\n🚀 SECTION {section + 1}: Attempting to progress...")
                
                # Fill any visible fields
                await self.fill_comprehensive_form(scenario)
                
                # Dismiss modals
                await self.dismiss_modals()
                
                # Take screenshot before submit
                await self.page.screenshot(path=f"section_{section + 1}_before_submit_{scenario['scenario_id']}.png")
                
                # Try to submit
                submit_button = await self.page.query_selector('button[type="submit"], input[type="submit"]')
                if not submit_button:
                    print("❌ No submit button found")
                    break
                
                await submit_button.click()
                await self.page.wait_for_timeout(3000)
                
                # Handle post-submit modals
                await self.dismiss_modals()
                
                await self.page.wait_for_load_state("networkidle", timeout=15000)
                
                # Take screenshot after submit
                await self.page.screenshot(path=f"section_{section + 1}_after_submit_{scenario['scenario_id']}.png")
                
                # Check if we've reached applicant/income section
                page_text = await self.page.text_content('body')
                
                # Look for indicators we've reached the right section
                income_indicators = ['income', 'salary', 'employment', 'applicant details', 'personal details']
                if any(indicator in page_text.lower() for indicator in income_indicators):
                    # Check for actual income fields
                    income_fields = await self.page.query_selector_all('input[name*="income"], input[name*="salary"], input[name*="net_profit"]')
                    if len(income_fields) > 0:
                        print(f"🎉 SUCCESS! Reached income section with {len(income_fields)} income fields!")
                        return True
                
                print(f"⚠️ Section {section + 1} completed, continuing...")
                await self.page.wait_for_timeout(2000)
            
            print("⚠️ Completed maximum sections without finding income fields")
            return False
            
        except Exception as e:
            print(f"❌ Error progressing through sections: {e}")
            return False
    
    async def fill_income_fields(self, scenario: Dict) -> bool:
        """Fill income fields based on employment type."""
        try:
            print("💰 Filling income fields...")
            
            income_amount = scenario['applicant1_income']
            
            # Look for all income-related fields
            income_selectors = [
                'input[name*="income"]',
                'input[name*="salary"]',
                'input[name*="net_profit"]',
                'input[name*="basic"]',
                'input[name*="employed"]'
            ]
            
            income_fields = []
            for selector in income_selectors:
                fields = await self.page.query_selector_all(selector)
                for field in fields:
                    if await field.is_visible():
                        name = await field.get_attribute('name')
                        income_fields.append((field, name))
            
            print(f"Found {len(income_fields)} visible income fields")
            
            filled_count = 0
            
            if scenario['applicant1_employment'] == 'employed':
                # Fill employed income fields
                for field, name in income_fields:
                    try:
                        await field.fill(str(income_amount))
                        print(f"✅ Filled {name} with £{income_amount:,}")
                        filled_count += 1
                    except:
                        pass
            
            else:
                # Fill self-employed income fields with pattern
                year1_amount = income_amount
                year2_amount = income_amount // 2
                year3_amount = 0
                
                for field, name in income_fields:
                    try:
                        if 'year_1' in name.lower() or 'last' in name.lower():
                            await field.fill(str(year1_amount))
                            print(f"✅ Filled {name} (Year 1) with £{year1_amount:,}")
                        elif 'year_2' in name.lower():
                            await field.fill(str(year2_amount))
                            print(f"✅ Filled {name} (Year 2) with £{year2_amount:,}")
                        elif 'year_3' in name.lower():
                            await field.fill(str(year3_amount))
                            print(f"✅ Filled {name} (Year 3) with £{year3_amount:,}")
                        else:
                            await field.fill(str(year1_amount))
                            print(f"✅ Filled {name} with £{year1_amount:,}")
                        
                        filled_count += 1
                    except:
                        pass
            
            print(f"📊 Successfully filled {filled_count} income fields")
            return filled_count > 0
            
        except Exception as e:
            print(f"❌ Error filling income: {e}")
            return False
    
    async def submit_and_extract_results(self, scenario: Dict) -> Dict[str, float]:
        """Submit final form and extract results."""
        try:
            print("🚀 Final submission and results extraction...")
            
            # Final submit
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
        """Extract lender results from the page."""
        try:
            print("📊 Extracting lender results...")
            results = {}
            
            page_text = await self.page.text_content('body')
            
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
    
    async def run_scenario(self, scenario: Dict) -> Dict[str, float]:
        """Run complete scenario."""
        try:
            print(f"\\n🎯 === RUNNING SCENARIO: {scenario['scenario_id']} ===")
            print(f"Type: {scenario['applicant_type']}")
            print(f"Income: £{scenario['applicant1_income']:,}")
            print(f"Employment: {scenario['applicant1_employment']}")
            
            # Create case
            if not await self.create_new_case(scenario):
                return {}
            
            # Progress through all sections
            if not await self.progress_through_sections(scenario):
                print("❌ Could not reach income section")
                return {}
            
            # Fill income fields
            if not await self.fill_income_fields(scenario):
                print("❌ Could not fill income fields")
                return {}
            
            # Submit and get results
            results = await self.submit_and_extract_results(scenario)
            
            return results
            
        except Exception as e:
            print(f"❌ Error running scenario: {e}")
            return {}
    
    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()


# Test function
async def test_complete_automation():
    """Test the complete automation."""
    mbt = MBTAutomationComplete()
    
    try:
        await mbt.start_browser(headless=False)
        
        if not await mbt.login():
            print("Login failed")
            return
        
        # Test scenario
        test_scenario = {
            'scenario_id': 'joint_employed_40k',
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
            print(f"\\n🎉 SUCCESS - Results for {test_scenario['scenario_id']}:")
            for lender, amount in results.items():
                print(f"   {lender}: £{amount:,.0f}")
        else:
            print(f"\\n❌ No results obtained")
    
    finally:
        print("\\n⏳ Keeping browser open for inspection...")
        await asyncio.sleep(60)
        await mbt.close()


if __name__ == "__main__":
    asyncio.run(test_complete_automation())