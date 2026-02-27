"""Detailed test of context matching logic."""

def find_and_replace_with_context_debug(text, mapping):
    """
    Find and replace text using context matching.
    DEBUG VERSION WITH PRINT STATEMENTS
    """
    original = mapping.get('original')
    left_context = mapping.get('leftContext', '')
    right_context = mapping.get('rightContext', '')
    occurrence_index = mapping.get('occurrenceIndex', 1)
    field = mapping.get('field')
    
    print(f"\n=== Searching for field '{field}' ===")
    print(f"  original: '{original}'")
    print(f"  left_context: '{left_context}'")
    print(f"  right_context: '{right_context}'")
    print(f"  occurrence_index: {occurrence_index}")
    
    if not original:
        return False, -1
    
    best_match_idx = -1
    match_count = 0
    search_start = 0
    
    while True:
        # Find next occurrence of original text
        idx = text.find(original, search_start)
        if idx == -1:
            print(f"  No more occurrences found after position {search_start}")
            break
        
        print(f"\n  Found '{original}' at position {idx}")
        
        # Check if this match has the right context
        context_matches = True
        
        # Check left context
        if left_context:
            check_start = max(0, idx - len(left_context))
            actual_left = text[check_start:idx]
            print(f"    Left check: actual='{actual_left}' vs expected='{left_context}'")
            if not (left_context in actual_left or actual_left.endswith(left_context)):
                context_matches = False
                print(f"      -> LEFT MISMATCH")
            else:
                print(f"      -> LEFT OK")
        
        # Check right context
        if right_context and context_matches:
            check_end = min(len(text), idx + len(original) + len(right_context))
            actual_right = text[idx + len(original):check_end]
            print(f"    Right check: actual='{actual_right}' vs expected='{right_context}'")
            if not (right_context in actual_right or actual_right.startswith(right_context)):
                context_matches = False
                print(f"      -> RIGHT MISMATCH")
            else:
                print(f"      -> RIGHT OK")
        
        if context_matches:
            match_count += 1
            print(f"    CONTEXT MATCH! This is match #{match_count}")
            if match_count == occurrence_index:
                best_match_idx = idx
                print(f"    This is the one we want! Returning position {idx}")
                break
        
        search_start = idx + 1
    
    return best_match_idx != -1, best_match_idx

# Test with the actual text
test_content = """Report for: ACME Corp
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

for mapping in mappings:
    found, idx = find_and_replace_with_context_debug(test_content, mapping)
    print(f"\n  Result: found={found}, idx={idx}\n")
