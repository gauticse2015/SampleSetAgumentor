"""Debug context matching"""

test_content = """Report for: ACME Corp
Company: ACME Corp
Address: 123 Main St
Company Website: www.acmecorp.com
Contact Company: ACME Corp"""

text = test_content

# Find all occurrences of "ACME Corp"
original = "ACME Corp"
idx = 0
count = 0
while True:
    idx = text.find(original, idx)
    if idx == -1:
        break
    count += 1
    
    # Show context
    left_start = max(0, idx - 50)
    right_end = min(len(text), idx + len(original) + 50)
    
    left_context = text[left_start:idx]
    right_context = text[idx + len(original):right_end]
    
    print(f"\nOccurrence {count}:")
    print(f"  Position: {idx}")
    print(f"  Left context (last 50): '{left_context}'")
    print(f"  Match: '{text[idx:idx+len(original)]}'")
    print(f"  Right context (next 50): '{right_context}'")
    
    idx += 1

# Now test the mappings
mappings = [
    {
        "original": "ACME Corp",
        "field": "company_name",
        "leftContext": "Report for: ",
        "rightContext": "\nCompany:",
        "occurrenceIndex": 1
    },
    {
        "original": "ACME Corp",
        "field": "company_name_2",
        "leftContext": "Company: ",
        "rightContext": "\nAddress:",
        "occurrenceIndex": 1
    },
    {
        "original": "ACME Corp",
        "field": "company_name_3",
        "leftContext": "Contact ",
        "rightContext": "",
        "occurrenceIndex": 1
    }
]

print("\n\n=== Testing Context Matching ===\n")

for mapping in mappings:
    original = mapping['original']
    left_context = mapping.get('leftContext', '')
    right_context = mapping.get('rightContext', '')
    
    print(f"Mapping: field={mapping['field']}")
    print(f"  Looking for: '{original}'")
    print(f"  Left context: '{left_context}'")
    print(f"  Right context: '{right_context}'")
    
    # Try to find it
    idx = 0
    match_count = 0
    while True:
        idx = text.find(original, idx)
        if idx == -1:
            break
        
        # Check context
        context_matches = True
        
        if left_context:
            check_start = max(0, idx - len(left_context))
            actual_left = text[check_start:idx]
            print(f"    Checking left: actual='{actual_left}', expected contains='{left_context}'")
            if not (left_context in actual_left or actual_left.endswith(left_context)):
                context_matches = False
                print(f"      LEFT CONTEXT MISMATCH")
        
        if right_context and context_matches:
            check_end = min(len(text), idx + len(original) + len(right_context))
            actual_right = text[idx + len(original):check_end]
            print(f"    Checking right: actual='{actual_right}', expected contains='{right_context}'")
            if not (right_context in actual_right or actual_right.startswith(right_context)):
                context_matches = False
                print(f"      RIGHT CONTEXT MISMATCH")
        
        if context_matches:
            match_count += 1
            print(f"    MATCH #{match_count}")
            if match_count == mapping.get('occurrenceIndex', 1):
                print(f"    FOUND at position {idx}")
                break
        
        idx += 1
    print()
