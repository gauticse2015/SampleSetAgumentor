import sys
import os
from app.utils.text_augmentor import TextAugmentor, _WORDNET_AVAILABLE

print(f"WordNet Available: {_WORDNET_AVAILABLE}")

if not _WORDNET_AVAILABLE:
    print("EXITING: WordNet not available")
    sys.exit(0)

aug = TextAugmentor()
text = "The happy dog runs fast in the park."
print(f"Original: {text}")

# Try 10 times with default settings (p=0.3)
for i in range(10):
    res = aug.process_text(text, ['synonym'], lang='eng')
    # res is list of tuples, index 1 is synonym result
    # [('original', text)] was removed, so index 0 is synonym result
    syn_text = res[0][1]
    print(f"Attempt {i+1}: {syn_text}")
    if syn_text != text:
        print("  -> CHANGED")
    else:
        print("  -> SAME")
