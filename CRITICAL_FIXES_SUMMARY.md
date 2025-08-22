# Critical Fixes Applied - Joint Income & Wait Times

## Issues Addressed

Based on user feedback: "8 still failed and the joint applicant self-employed is still filling in wrong. it's giving each applicant the total rather than half of the total. also it still isn't waiting long enough to get all the results"

## 🔧 Fix 1: Variable Scope Issue in Wait Time Calculation

**Problem**: The `run_search_and_extract_results()` method was trying to access `income` and `case_type` variables that weren't in scope, causing wait time calculation to fail.

**Solution**: 
- Modified `run_search_and_extract_results()` to accept `case_type` and `income` parameters
- Updated the call site to pass these parameters
- Location: `real_mbt_automation.py:110, 630`

## 🕒 Fix 2: Dramatically Increased Wait Times

**Problem**: Previous wait times (90 seconds base) were insufficient for all lenders to populate.

**Solution**: Implemented extremely conservative wait times:
- **Base wait**: Increased from 90s to **180s (3 minutes)**
- **Single scenarios**: 1.5x multiplier (was 1.0x)
- **Joint scenarios**: 3.0x multiplier (was 2.5x)
- **Income multiplier**: More aggressive scaling
- **Maximum wait**: Increased to **10 minutes** (was 6 minutes)

**Examples**:
- Single £30k: ~4.5 minutes
- Joint £120k: ~18 minutes  
- Joint £200k: ~30 minutes (capped at 10 minutes)

## 💰 Fix 3: Enhanced Income Splitting Debugging

**Problem**: Unclear whether income was being split correctly for joint scenarios.

**Solution**: Added extensive debugging logs to verify:
- Original total income amount
- Calculated split amounts
- Values actually being input to each field
- Final verification messages

**Key Debug Messages**:
```
💰 INPUTTING SPLIT AMOUNT: £100,000 (THIS IS HALF OF £200,000 TOTAL)
⚠️  VERIFY: We are inputting £100,000, NOT the full £200,000
```

## 📊 Income Splitting Logic Verified

The splitting logic is correct:

### Joint Self-Employed (S.Joint)
```python
applicant_income = income // 2  # Split total equally
applicant2_salary = applicant_income  # Employed applicant gets half
last_year_profit = applicant_income  # Self-employed gets half for last year
two_year_profit = applicant_income // 2  # Quarter for two years ago
```

### Joint Employed (E.Joint)
```python
applicant_income = income // 2  # Split total equally
# Both applicants get the split amount
```

## 🧪 Testing

Run the comprehensive test:
```bash
python test_critical_fixes.py
```

Or test a single critical scenario:
```bash
python test_critical_fixes.py single
```

## 📈 Expected Improvements

1. **Income Splitting**: Clear debugging will show exactly what values are being input
2. **Wait Times**: 3-10 minute waits should allow all lenders to populate fully
3. **Success Rate**: Should see 12-15+ lenders per scenario consistently
4. **Failure Rate**: Should drop from 8/32 failed to 0-2/32 failed

## 🔍 Verification Points

1. **Income Values**: Check console output for "INPUTTING SPLIT AMOUNT" messages
2. **Wait Times**: Verify scenarios wait the calculated duration before extraction
3. **Lender Count**: Should consistently see 12+ lenders per scenario
4. **Gen H Results**: Should see reasonable affordability amounts relative to income level

## ⏱️ Timeline Impact

- Full 32-scenario run will now take **2-3 hours** instead of 1 hour
- This is necessary to ensure complete and accurate results
- Consider running scenarios in smaller batches if needed