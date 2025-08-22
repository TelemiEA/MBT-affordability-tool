"""
Systematic Required Fields Automation
Focus on identifying and filling ALL required fields (red asterisk) before submission
Work from top to bottom systematically
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def systematic_required_fields():
    """Systematically identify and fill all required fields before submission."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1500)
        page = await browser.new_page()
        page.set_default_timeout(45000)  # Longer timeout
        
        try:
            print("🎯 SYSTEMATIC REQUIRED FIELDS AUTOMATION")
            print("Strategy: Find ALL required fields (red asterisk) and fill systematically")
            print("=" * 70)
            
            # === SETUP ===
            await page.goto("https://mortgagebrokertools.co.uk/signin")
            await page.wait_for_load_state("networkidle")
            
            await page.fill('input[name="email"]', os.getenv("MBT_USERNAME"))
            await page.fill('input[name="password"]', os.getenv("MBT_PASSWORD"))
            await page.click('input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            print("✅ Login successful")
            
            await page.goto('https://mortgagebrokertools.co.uk/dashboard/quotes')
            await page.wait_for_load_state("networkidle")
            await page.click('text=Create RESI Case')
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)
            print("✅ Case created")
            
            # === BASIC FIELDS ===
            await page.fill('input[name="firstname"]', 'Test')
            await page.fill('input[name="surname"]', 'User')
            await page.fill('input[name="email"]', 'test@example.com')
            await page.fill('input[name="purchase"]', '1000000')
            await page.fill('input[name="loan_amount"]', '100000')
            
            # Joint application
            joint_checkbox = await page.query_selector('input[type="checkbox"]')
            is_joint = False
            if joint_checkbox:
                await joint_checkbox.check()
                is_joint = True
                await page.wait_for_timeout(2000)
                print("✅ Joint application selected")
            
            await submit_and_continue(page, "Basic application")
            
            # === SYSTEMATIC SECTION PROCESSING ===
            section_count = 0
            max_sections = 15
            
            while section_count < max_sections:
                section_count += 1
                print(f"\n📋 SECTION {section_count}: SYSTEMATIC REQUIRED FIELD ANALYSIS")
                print("-" * 60)
                
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(2000)
                
                # Take screenshot of current state
                await page.screenshot(path=f"section_{section_count}_start.png")
                
                # Check if we've reached results
                page_text = await page.text_content('body')
                current_url = page.url
                print(f"Current URL: {current_url}")
                
                if any(keyword in page_text.lower() for keyword in ['results', 'lender', 'quote', 'offers']):
                    print("🎉 RESULTS SECTION DETECTED!")
                    await page.screenshot(path="SYSTEMATIC_RESULTS_FOUND.png")
                    
                    results = await extract_results(page)
                    if results:
                        print(f"\n🎉🎉🎉 SYSTEMATIC AUTOMATION SUCCESS! 🎉🎉🎉")
                        print(f"📊 LENDERS EXTRACTED: {list(results.keys())}")
                        print(f"📈 TOTAL: {len(results)}")
                        return results
                    else:
                        print("✅ Reached results page")
                        return {}
                
                # === IDENTIFY ALL REQUIRED FIELDS ===
                required_fields = await identify_required_fields(page)
                print(f"🔍 Found {len(required_fields)} required fields:")
                
                for i, field_info in enumerate(required_fields):
                    print(f"   {i+1}. {field_info['label']} ({field_info['type']})")
                
                if not required_fields:
                    print("ℹ️ No required fields detected - submitting section")
                    await submit_and_continue(page, f"Section {section_count}")
                    continue
                
                # === FILL REQUIRED FIELDS SYSTEMATICALLY ===
                print(f"\n📝 FILLING {len(required_fields)} REQUIRED FIELDS SYSTEMATICALLY:")
                
                filled_count = 0
                for i, field_info in enumerate(required_fields):
                    print(f"\n   Field {i+1}/{len(required_fields)}: {field_info['label']}")
                    
                    success = await fill_required_field(field_info, page, is_joint)
                    if success:
                        filled_count += 1
                        print(f"   ✅ Completed: {field_info['label']}")
                    else:
                        print(f"   ⚠️ Unable to complete: {field_info['label']}")
                    
                    await page.wait_for_timeout(1000)  # Brief pause between fields
                
                print(f"\n📊 SECTION {section_count} SUMMARY:")
                print(f"   Required fields found: {len(required_fields)}")
                print(f"   Successfully filled: {filled_count}")
                print(f"   Completion rate: {(filled_count/len(required_fields)*100):.1f}%" if required_fields else "N/A")
                
                # Take screenshot after filling
                await page.screenshot(path=f"section_{section_count}_completed.png")
                
                # Submit section
                print(f"\n🚀 Submitting Section {section_count}...")
                await submit_and_continue(page, f"Section {section_count}")
                
                # Brief pause before next section
                await page.wait_for_timeout(2000)
            
            print(f"\n⚠️ Completed {max_sections} sections without finding results")
            await page.screenshot(path="systematic_max_sections_reached.png")
            return {}
            
        except Exception as e:
            print(f"❌ Systematic automation error: {e}")
            await page.screenshot(path="systematic_error.png")
            return {}
            
        finally:
            print("\n⏳ Keeping browser open for inspection...")
            await page.wait_for_timeout(60000)  # 1 minute
            await browser.close()


async def identify_required_fields(page):
    """Identify all required fields marked with red asterisk."""
    try:
        print("🔍 Scanning page for required fields (red asterisk)...")
        
        # JavaScript to find required fields
        required_fields_js = """
        {
            const requiredFields = [];
            
            // Look for elements with red asterisk or required markers
            const possibleMarkers = document.querySelectorAll('*');
            
            possibleMarkers.forEach(element => {
                const text = element.textContent || '';
                const style = window.getComputedStyle(element);
                const color = style.color;
                
                // Check for red asterisk markers
                if ((text.includes('*') || element.innerHTML.includes('*')) && 
                    (color.includes('red') || color.includes('rgb(255') || 
                     element.style.color.includes('red') ||
                     element.className.includes('required') ||
                     element.className.includes('error'))) {
                    
                    // Find associated form field
                    let associatedField = null;
                    let fieldType = 'unknown';
                    let label = text.replace('*', '').trim();
                    
                    // Look for nearby input, select, or textarea elements
                    const parent = element.closest('div, fieldset, .form-group, .field');
                    if (parent) {
                        // Check for input fields
                        const input = parent.querySelector('input, select, textarea');
                        if (input) {
                            associatedField = input;
                            fieldType = input.tagName.toLowerCase();
                            if (input.type) fieldType += '-' + input.type;
                        }
                    }
                    
                    // Also check siblings
                    if (!associatedField) {
                        const siblings = element.parentElement?.querySelectorAll('input, select, textarea') || [];
                        if (siblings.length > 0) {
                            associatedField = siblings[0];
                            fieldType = associatedField.tagName.toLowerCase();
                            if (associatedField.type) fieldType += '-' + associatedField.type;
                        }
                    }
                    
                    if (associatedField && associatedField.offsetParent !== null) {
                        const rect = associatedField.getBoundingClientRect();
                        requiredFields.push({
                            label: label,
                            type: fieldType,
                            element: associatedField,
                            bounds: {
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height
                            },
                            name: associatedField.name || '',
                            id: associatedField.id || '',
                            placeholder: associatedField.placeholder || '',
                            visible: associatedField.offsetParent !== null
                        });
                    }
                }
            });
            
            // Remove duplicates based on element position
            const uniqueFields = [];
            const seen = new Set();
            
            requiredFields.forEach(field => {
                const key = `${field.bounds.x}-${field.bounds.y}-${field.type}`;
                if (!seen.has(key)) {
                    seen.add(key);
                    uniqueFields.push(field);
                }
            });
            
            // Sort by vertical position (top to bottom)
            uniqueFields.sort((a, b) => a.bounds.y - b.bounds.y);
            
            return uniqueFields.map(field => ({
                label: field.label,
                type: field.type,
                name: field.name,
                id: field.id,
                placeholder: field.placeholder,
                bounds: field.bounds,
                visible: field.visible
            }));
        }
        """
        
        required_fields = await page.evaluate(required_fields_js)
        return required_fields
        
    except Exception as e:
        print(f"⚠️ Error identifying required fields: {e}")
        return []


async def fill_required_field(field_info, page, is_joint):
    """Fill a specific required field based on its type and label."""
    try:
        field_type = field_info['type']
        label = field_info['label'].lower()
        
        # Click on the field's position to focus it
        bounds = field_info['bounds']
        center_x = bounds['x'] + bounds['width'] / 2
        center_y = bounds['y'] + bounds['height'] / 2
        
        print(f"      Targeting {field_type} at ({center_x:.0f}, {center_y:.0f})")
        
        # Handle different field types
        if 'select' in field_type or 'dropdown' in label:
            return await fill_dropdown_field(center_x, center_y, label, page)
        
        elif 'input-text' in field_type or 'input-email' in field_type:
            return await fill_text_field(center_x, center_y, label, page)
        
        elif 'input-number' in field_type:
            return await fill_number_field(center_x, center_y, label, page, is_joint)
        
        elif 'input-date' in field_type or 'date' in label or 'birth' in label:
            return await fill_date_field(center_x, center_y, page)
        
        elif 'input-radio' in field_type or 'radio' in label:
            return await fill_radio_field(center_x, center_y, label, page)
        
        elif 'input-checkbox' in field_type:
            return await fill_checkbox_field(center_x, center_y, page)
        
        else:
            print(f"      Unknown field type: {field_type}")
            return False
            
    except Exception as e:
        print(f"      ⚠️ Error filling field: {e}")
        return False


async def fill_dropdown_field(x, y, label, page):
    """Fill dropdown field using coordinate-based clicking."""
    try:
        # Click on dropdown
        await page.mouse.click(x, y)
        await page.wait_for_timeout(1000)
        
        # Try to select appropriate option based on label
        if 'reason' in label and 'mortgage' in label:
            for option in ['First-time buyer', 'Purchase', 'Buy']:
                try:
                    await page.click(f'text={option}', timeout=2000)
                    return True
                except:
                    continue
        
        elif 'property' in label and 'type' in label:
            for option in ['Terraced House', 'House', 'Detached', 'Semi']:
                try:
                    await page.click(f'text={option}', timeout=2000)
                    return True
                except:
                    continue
        
        elif 'term' in label or 'mortgage' in label:
            for option in ['35', '35 years', '35 year']:
                try:
                    await page.click(f'text={option}', timeout=2000)
                    return True
                except:
                    continue
        
        elif 'marital' in label or 'married' in label:
            for option in ['Single', 'Married', 'Divorced']:
                try:
                    await page.click(f'text={option}', timeout=2000)
                    return True
                except:
                    continue
        
        elif 'country' in label or 'residence' in label:
            for option in ['England', 'United Kingdom', 'UK']:
                try:
                    await page.click(f'text={option}', timeout=2000)
                    return True
                except:
                    continue
        
        elif 'employment' in label or 'status' in label:
            for option in ['Employed', 'Employment']:
                try:
                    await page.click(f'text={option}', timeout=2000)
                    return True
                except:
                    continue
        
        elif 'residential' in label or 'tenant' in label:
            for option in ['Tenant', 'Renting', 'Private Tenant']:
                try:
                    await page.click(f'text={option}', timeout=2000)
                    return True
                except:
                    continue
        
        # Fallback: double-click same spot (your suggested technique)
        await page.mouse.click(x, y)
        await page.wait_for_timeout(1000)
        await page.mouse.click(x, y)
        await page.wait_for_timeout(1000)
        
        return True
        
    except Exception as e:
        print(f"      Dropdown error: {e}")
        return False


async def fill_text_field(x, y, label, page):
    """Fill text field."""
    try:
        await page.mouse.click(x, y)
        await page.wait_for_timeout(500)
        
        if 'email' in label:
            await page.keyboard.type('test@example.com')
        elif 'name' in label:
            await page.keyboard.type('Test')
        elif 'postcode' in label:
            await page.keyboard.type('SW1A 1AA')
        elif 'phone' in label or 'mobile' in label:
            await page.keyboard.type('07123456789')
        else:
            await page.keyboard.type('Test')
        
        return True
        
    except Exception as e:
        print(f"      Text field error: {e}")
        return False


async def fill_number_field(x, y, label, page, is_joint):
    """Fill number field."""
    try:
        await page.mouse.click(x, y)
        await page.wait_for_timeout(500)
        
        if 'income' in label or 'salary' in label:
            await page.keyboard.type('40000')
        elif 'child' in label or 'dependent' in label:
            await page.keyboard.type('0')
        elif 'adult' in label or 'applicant' in label:
            value = '2' if is_joint else '1'
            await page.keyboard.type(value)
        elif 'age' in label:
            await page.keyboard.type('30')
        elif any(word in label for word in ['council', 'tax', 'insurance', 'expense']):
            await page.keyboard.type('0')
        else:
            await page.keyboard.type('0')
        
        return True
        
    except Exception as e:
        print(f"      Number field error: {e}")
        return False


async def fill_date_field(x, y, page):
    """Fill date field with 01-01-1990."""
    try:
        await page.mouse.click(x, y)
        await page.wait_for_timeout(500)
        
        # Try different date formats
        for date_format in ['01/01/1990', '1990-01-01', '01-01-1990']:
            try:
                await page.keyboard.fill_text('')  # Clear first
                await page.keyboard.type(date_format)
                await page.wait_for_timeout(500)
                break
            except:
                continue
        
        return True
        
    except Exception as e:
        print(f"      Date field error: {e}")
        return False


async def fill_radio_field(x, y, label, page):
    """Fill radio button field."""
    try:
        # For radio buttons, just click the coordinates
        await page.mouse.click(x, y)
        await page.wait_for_timeout(500)
        return True
        
    except Exception as e:
        print(f"      Radio field error: {e}")
        return False


async def fill_checkbox_field(x, y, page):
    """Fill checkbox field."""
    try:
        await page.mouse.click(x, y)
        await page.wait_for_timeout(500)
        return True
        
    except Exception as e:
        print(f"      Checkbox error: {e}")
        return False


async def submit_and_continue(page, section_name):
    """Submit current section and handle any modals."""
    try:
        print(f"🚀 Submitting {section_name}...")
        
        # Find submit button
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
        if submit_button:
            await submit_button.click()
            await page.wait_for_timeout(3000)
            
            # Handle modal if it appears
            try:
                modal_button = await page.query_selector('button:has-text("OK")')
                if modal_button and await modal_button.is_visible():
                    await modal_button.click()
                    await page.wait_for_timeout(2000)
                    print(f"   ✅ {section_name} modal handled")
            except:
                pass
            
            await page.wait_for_load_state("networkidle")
            print(f"   ✅ {section_name} submitted successfully")
        else:
            print(f"   ⚠️ No submit button found for {section_name}")
            
    except Exception as e:
        print(f"   ⚠️ Submit error for {section_name}: {e}")


async def extract_results(page):
    """Extract lender results if on results page."""
    try:
        print("📊 Extracting results...")
        
        page_text = await page.text_content('body')
        target_lenders = ["Gen H", "Accord", "Skipton", "Kensington", "Precise", "Atom"]
        
        results = {}
        for lender in target_lenders:
            if lender in page_text:
                results[lender] = "Found"  # Simplified for now
        
        return results
        
    except Exception as e:
        print(f"❌ Results extraction error: {e}")
        return {}


if __name__ == "__main__":
    print("🎯 SYSTEMATIC REQUIRED FIELDS AUTOMATION")
    print("Focus: Identify ALL required fields before submission")
    print("=" * 60)
    
    results = asyncio.run(systematic_required_fields())
    
    if results:
        print(f"\n🎉 AUTOMATION COMPLETE!")
        print(f"Results: {results}")
    else:
        print("\n📊 Automation completed - check screenshots for progress")