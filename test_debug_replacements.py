"""Debug replacement finding."""

text = """Report for: ACME Corp
Company: ACME Corp
Address: 123 Main St
Company Website: www.acmecorp.com
Contact Company: ACME Corp"""

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

replacements = []

for i, mapping in enumerate(mappings):
    original = mapping.get('original')
    left_context = mapping.get('leftContext', '')
    right_context = mapping.get('rightContext', '')
    occurrence_index = mapping.get('occurrenceIndex', 1)
    field = mapping.get('field')
    value = f"VALUE_{field}"
    
    print(f"\nSearching for mapping {i}: {field}")
    
    best_match_idx = -1
    match_count = 0
    search_start = 0
    
    while True:
        idx = text.find(original, search_start)
        if idx == -1:
            break
        
        print(f"  Found '{original}' at position {idx}")
        
        # Check context
        context_matches = True
        
        if left_context:
            check_start = max(0, idx - len(left_context) * 2)
            actual_left = text[check_start:idx]
            print(f"    Left context check: '{left_context}' in '{actual_left}'?", end=" ")
            if left_context not in actual_left:
                context_matches = False
                print("NO")
            else:
                print("YES")
        
        if right_context and context_matches:
            check_end = min(len(text), idx + len(original) + len(right_context) * 2)
            actual_right = text[idx + len(original):check_end]
            print(f"    Right context check: '{right_context}' in '{actual_right}'?", end=" ")
            if right_context not in actual_right:
                context_matches = False
                print("NO")
            else:
                print("YES")
        
        if context_matches:
            match_count += 1
            print(f"    MATCH! This is match #{match_count}")
            if match_count == occurrence_index:
                best_match_idx = idx
                print(f"    Found the one we want at position {idx}")
                break
        
        search_start = idx + 1
    
    if best_match_idx != -1:
        replacements.append((best_match_idx, len(original), value, i))
        print(f"  -> Will replace at position {best_match_idx}")
    else:
        print(f"  -> NOT FOUND")

print(f"\n\nAll replacements to make: {replacements}")
print(f"Sorted by position (descending): {sorted(replacements, key=lambda x: x[0], reverse=True)}")

# Apply replacements
replacements_sorted = sorted(replacements, key=lambda x: x[0], reverse=True)
for pos, original_len, value, mapping_idx in replacements_sorted:
    print(f"\nReplacing at position {pos}: '{text[pos:pos+original_len]}' -> '{value}'")
    text = text[:pos] + value + text[pos + original_len:]
    print(f"Result: {text[:80]}...")

print(f"\n\nFinal text:\n{text}")
