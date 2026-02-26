import random
import re
import string
import os

# ---------------------------------------------------------------------------
# NLTK / WordNet bootstrap
# ---------------------------------------------------------------------------
# We check multiple candidate locations for the nltk_data directory to ensure
# it works in various environments (local dev, Docker, etc.).

_CANDIDATE_PATHS = [
    # 1. Project root relative to this file (app/utils/text_augmentor.py -> root/nltk_data)
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nltk_data')),
    # 2. Standard Docker path
    '/app/nltk_data',
    # 3. Current working directory
    os.path.join(os.getcwd(), 'nltk_data'),
]

_NLTK_DATA_DIR = _CANDIDATE_PATHS[0]  # Default fallback
for path in _CANDIDATE_PATHS:
    if os.path.isdir(path) and os.path.isdir(os.path.join(path, 'corpora')):
        _NLTK_DATA_DIR = path
        break

# Expose the path via the NLTK_DATA environment variable
os.environ.setdefault('NLTK_DATA', _NLTK_DATA_DIR)

try:
    import nltk
    # Prepend our discovered data dir so it takes priority
    if _NLTK_DATA_DIR not in nltk.data.path:
        nltk.data.path.insert(0, _NLTK_DATA_DIR)
    
    from nltk.corpus import wordnet as _wordnet
    
    # Quick probe – raises LookupError if the corpus files are missing.
    try:
        _wordnet.synsets('test')
        _WORDNET_AVAILABLE = True
    except LookupError:
        print(
            f"[TextAugmentor] WARNING: WordNet data not found.\n"
            f"  Searched paths: {_CANDIDATE_PATHS}\n"
            f"  Selected path: {_NLTK_DATA_DIR}\n"
            f"  Fix: run 'python -m nltk.downloader -d nltk_data wordnet omw-1.4' in project root.\n"
            f"  Synonym replacement is disabled."
        )
        _WORDNET_AVAILABLE = False
except ImportError:
    print("[TextAugmentor] WARNING: nltk package not installed. Run: pip install nltk")
    _WORDNET_AVAILABLE = False
except Exception as _e:
    print(f"[TextAugmentor] WARNING: WordNet unavailable ({_e}). Synonym replacement disabled.")
    _WORDNET_AVAILABLE = False

# ---------------------------------------------------------------------------
# Supported languages
# ---------------------------------------------------------------------------
# Maps human-readable names (shown in the UI) to ISO 639-3 codes understood
# by NLTK's Open Multilingual WordNet (OMW-1.4).
SUPPORTED_LANGUAGES = {
    'English':             'eng',
    'Spanish':             'spa',
    'French':              'fra',
    'Italian':             'ita',
    'Portuguese':          'por',
    'Dutch':               'nld',
    'Polish':              'pol',
    'Finnish':             'fin',
    'Japanese':            'jpn',
    'Chinese (Mandarin)':  'cmn',
    'Arabic':              'arb',
    'Indonesian':          'ind',
    'Thai':                'tha',
    'Croatian':            'hrv',
    'Slovenian':           'slv',
    'Bulgarian':           'bul',
    'Danish':              'dan',
    'Swedish':             'swe',
    'Greek':               'ell',
    'Hebrew':              'heb',
    'Persian':             'fas',
    'Catalan':             'cat',
    'Basque':              'eus',
    'Galician':            'glg',
    'Malay':               'zsm',
    'Albanian':            'als',
    'Romanian':            'ron',
    'Lithuanian':          'lit',
    'Slovak':              'slk',
    'Icelandic':           'isl',
    'Norwegian (Bokmål)':  'nob',
    'Norwegian (Nynorsk)': 'nno',
}

class TextAugmentor:
    """Text augmentation class providing various text transformation techniques."""
    
    def __init__(self):
        pass
    
    def process_text(self, text, operations, lang='eng'):
        """
        Apply selected text augmentation operations.
        
        Args:
            text: Input text string
            operations: List of augmentation operations to apply
            lang: ISO 639-3 language code for synonym replacement (default 'eng')
            
        Returns:
            List of (augmentation_type, text) tuples
        """
        augmented_results = []
        
        if 'synonym' in operations:
            # Simple synonym replacement (word substitutions)
            synonym_text = self._synonym_replace(text, lang=lang)
            augmented_results.append(("synonym", synonym_text))
            
        if 'random_insert' in operations:
            # Random character insertion
            inserted_text = self._random_insert(text)
            augmented_results.append(("random_insert", inserted_text))
            
        if 'random_swap' in operations:
            # Random word swap
            swapped_text = self._random_swap(text)
            augmented_results.append(("random_swap", swapped_text))
            
        if 'random_delete' in operations:
            # Random character deletion
            deleted_text = self._random_delete(text)
            augmented_results.append(("random_delete", deleted_text))
            
        if 'case_change' in operations:
            # Case variations
            for case_type, case_text in self._case_variations(text):
                augmented_results.append((f"case_{case_type}", case_text))
                
        if 'punctuation' in operations:
            # Punctuation manipulation
            punct_text = self._punctuation_manipulate(text)
            augmented_results.append(("punctuation", punct_text))
            
        if 'back_translation' in operations:
            # Simulate back-translation (simple word order shuffle)
            back_trans_text = self._simulate_back_translation(text)
            augmented_results.append(("back_translation", back_trans_text))
            
        if 'spacing' in operations:
            # Random spacing variations
            spaced_text = self._random_spacing(text)
            augmented_results.append(("spacing", spaced_text))
            
        return augmented_results
    
    # ------------------------------------------------------------------
    # Synonym replacement – powered by NLTK WordNet + OMW-1.4
    # ------------------------------------------------------------------

    def _synonym_replace(self, text, lang='eng', aug_p=0.5):
        """
        Replace words with WordNet synonyms using NLTK + Open Multilingual
        WordNet (OMW-1.4).

        Supports 32 languages offline (see SUPPORTED_LANGUAGES).
        Falls back to the original text if NLTK data is unavailable.

        Args:
            text:  Input string.
            lang:  ISO 639-3 language code (default 'eng').
            aug_p: Probability that any eligible word is replaced (0-1).

        Returns:
            Augmented string.
        """
        if not _WORDNET_AVAILABLE:
            return text  # Graceful degradation

        words = text.split()
        if not words:
            return text

        result = []
        for word in words:
            # Strip surrounding punctuation for the lookup
            stripped = word.strip(string.punctuation)
            prefix = word[: len(word) - len(word.lstrip(string.punctuation))]
            suffix = word[len(word.rstrip(string.punctuation)):]

            replaced = False
            if stripped and random.random() < aug_p:
                candidate = self._get_wordnet_synonym(stripped, lang)
                if candidate and candidate.lower() != stripped.lower():
                    # Preserve original capitalisation
                    if stripped[0].isupper():
                        candidate = candidate.capitalize()
                    result.append(prefix + candidate + suffix)
                    replaced = True

            if not replaced:
                result.append(word)

        return ' '.join(result)

    @staticmethod
    def _get_wordnet_synonym(word, lang='eng'):
        """
        Return a random synonym for *word* in *lang* via WordNet/OMW,
        or None if no synonym is available.
        """
        try:
            synsets = _wordnet.synsets(word, lang=lang)
            if not synsets:
                return None

            # Collect all lemma names from all synsets, excluding the word itself
            synonyms = set()
            for synset in synsets:
                for lemma in synset.lemmas(lang=lang):
                    name = lemma.name().replace('_', ' ')
                    if name.lower() != word.lower():
                        synonyms.add(name)

            return random.choice(list(synonyms)) if synonyms else None
        except Exception:
            return None
    
    def _random_insert(self, text, n=2):
        """Randomly insert characters into words."""
        words = list(text)
        if not words:
            return text
            
        for _ in range(n):
            if len(words) > 1:
                pos = random.randint(0, len(words) - 1)
                char = random.choice(string.ascii_lowercase)
                words.insert(pos, char)
                
        return ''.join(words)
    
    def _random_swap(self, text):
        """Randomly swap adjacent words."""
        words = text.split()
        if len(words) < 2:
            return text
            
        # Swap 1-2 pairs of adjacent words
        num_swaps = min(random.randint(1, 2), len(words) // 2)
        for _ in range(num_swaps):
            idx = random.randint(0, len(words) - 2)
            words[idx], words[idx + 1] = words[idx + 1], words[idx]
            
        return ' '.join(words)
    
    def _random_delete(self, text, n=2):
        """Randomly delete characters from text."""
        words = list(text)
        if len(words) <= n:
            return text
            
        for _ in range(n):
            if len(words) > 1:
                pos = random.randint(0, len(words) - 1)
                words.pop(pos)
                
        return ''.join(words)
    
    def _case_variations(self, text):
        """Generate different case variations of the text."""
        variations = []
        
        # Upper case
        variations.append(('upper', text.upper()))
        
        # Lower case
        variations.append(('lower', text.lower()))
        
        # Title case
        variations.append(('title', text.title()))
        
        # Random mixed case
        mixed = ''.join(c.upper() if random.random() > 0.5 else c.lower() for c in text)
        variations.append(('mixed', mixed))
        
        return variations
    
    def _punctuation_manipulate(self, text):
        """Add or remove punctuation randomly."""
        # Remove some punctuation and add others
        text = re.sub(r'[.,;:!?]', lambda m: random.choice(['', m.group(), m.group() * 2]), text)
        
        # Add random punctuation at end if missing
        if text and text[-1] not in '.,;:!?':
            if random.random() > 0.5:
                text += random.choice(['.', '!', '?'])
                
        return text
    
    def _simulate_back_translation(self, text):
        """Simulate back-translation by shuffling phrases."""
        # Split by common delimiters
        phrases = re.split(r'([,;])', text)
        if len(phrases) > 2:
            # Shuffle phrases while keeping delimiters in place
            delimiters = phrases[1::2]
            content = phrases[0::2]
            random.shuffle(content)
            
            # Reconstruct
            result = []
            for i, c in enumerate(content):
                result.append(c)
                if i < len(delimiters):
                    result.append(delimiters[i])
            return ''.join(result)
        return text
    
    def _random_spacing(self, text):
        """Add random extra spaces."""
        words = text.split()
        if not words:
            return text
            
        result = []
        for word in words:
            result.append(word)
            # Randomly add extra spaces
            if random.random() > 0.7:
                result.append(' ' * random.randint(2, 4))
            else:
                result.append(' ')
                
        return ''.join(result).strip()
