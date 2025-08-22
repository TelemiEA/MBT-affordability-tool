"""
Test the case matching logic for credit scenarios
"""

# Test data from the logs
test_rows = [
    "QX002304221 RESI C . E-Single £100,000 15/08/25 - 12:41 pm",
    "QX002304304 RESI C . Self-Joint £100,000 15/08/25 - 10:46 am", 
    "QX002304287 RESI C . Self-Single £100,000 15/08/25 - 10:42 am",
    "QX002304261 RESI C . E-Joint £100,000 15/08/25 - 10:37 am"
]

test_cases = [
    "C . E-Single",
    "C . Self-Single", 
    "C . E-Joint",
    "C . Self-Joint"
]

print("🔍 Testing Case Matching Logic")
print("=" * 50)

for case_reference in test_cases:
    print(f"\n🎯 Looking for: '{case_reference}'")
    
    matches_found = []
    for i, row_text in enumerate(test_rows, 1):
        # Test the exact matching logic
        if 'QX' in row_text and case_reference in row_text:
            matches_found.append(f"Row {i}: {row_text}")
    
    if matches_found:
        print(f"   ✅ Found {len(matches_found)} matches:")
        for match in matches_found:
            print(f"      {match}")
    else:
        print(f"   ❌ No matches found")

print(f"\n" + "=" * 50)
print("🧪 Testing why exact matching might fail...")

# Test each case individually
for case_reference in test_cases:
    print(f"\n🔍 Testing: '{case_reference}'")
    for i, row_text in enumerate(test_rows, 1):
        contains_qx = 'QX' in row_text
        contains_case = case_reference in row_text
        print(f"   Row {i}: QX={contains_qx}, Case={contains_case} -> {row_text[:50]}...")
        if contains_qx and contains_case:
            print(f"      ✅ SHOULD MATCH!")
        else:
            print(f"      ❌ No match")