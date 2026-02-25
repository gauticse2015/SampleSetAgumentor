import os
import time
import random
import re
import string

class TextAugmentor:
    """Text augmentation class providing various text transformation techniques."""
    
    def __init__(self, output_path):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
    
    def process_text(self, text, operations):
        """
        Apply selected text augmentation operations.
        
        Args:
            text: Input text string
            operations: List of augmentation operations to apply
            
        Returns:
            List of augmented text strings (including original)
        """
        augmented_results = []
        
        # Always include the original text
        augmented_results.append(("original", text))
        
        if 'synonym' in operations:
            # Simple synonym replacement (word substitutions)
            synonym_text = self._synonym_replace(text)
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
    
    def save_augmentations(self, augmented_results, base_filename="text"):
        """
        Save augmented texts to separate files.
        
        Args:
            augmented_results: List of (augmentation_type, text) tuples
            base_filename: Base name for output files
            
        Returns:
            List of saved filenames
        """
        saved_files = []
        timestamp = int(time.time())
        
        for aug_type, text in augmented_results:
            filename = f"{base_filename}_{aug_type}_{timestamp}.txt"
            filepath = os.path.join(self.output_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            
            saved_files.append(filename)
            
        return saved_files
    
    def _synonym_replace(self, text, n=2):
        """Simple synonym replacement using a basic dictionary."""
        # Basic synonym dictionary
        synonyms = {
            'good': ['great', 'excellent', 'fine'],
            'bad': ['poor', 'terrible', 'awful'],
            'happy': ['joyful', 'cheerful', 'glad'],
            'sad': ['unhappy', 'sorrowful', 'melancholy'],
            'big': ['large', 'huge', 'enormous'],
            'small': ['tiny', 'little', 'miniature'],
            'fast': ['quick', 'rapid', 'swift'],
            'slow': ['sluggish', 'gradual', 'unhurried'],
            'beautiful': ['pretty', 'lovely', 'gorgeous'],
            'ugly': ['unattractive', 'unsightly', 'hideous'],
            'smart': ['intelligent', 'clever', 'brilliant'],
            'stupid': ['foolish', 'silly', 'unintelligent'],
            'love': ['adore', 'cherish', 'admire'],
            'hate': ['despise', 'loathe', 'detest'],
            'start': ['begin', 'commence', 'initiate'],
            'end': ['finish', 'conclude', 'terminate']
        }
        
        words = text.split()
        if not words:
            return text
            
        # Find words that have synonyms
        replaceable = [(i, word.lower().strip(string.punctuation)) 
                      for i, word in enumerate(words) 
                      if word.lower().strip(string.punctuation) in synonyms]
        
        if not replaceable:
            return text
            
        # Replace up to n words
        num_to_replace = min(n, len(replaceable))
        indices_to_replace = random.sample(replaceable, num_to_replace)
        
        for idx, word_lower in indices_to_replace:
            word = words[idx]
            punctuation = ''
            # Preserve punctuation
            while word and word[-1] in string.punctuation:
                punctuation = word[-1] + punctuation
                word = word[:-1]
            while word and word[0] in string.punctuation:
                word = word[1:]
                
            if word_lower in synonyms:
                new_word = random.choice(synonyms[word_lower])
                # Preserve original case
                if word[0].isupper():
                    new_word = new_word.capitalize()
                words[idx] = new_word + punctuation
                
        return ' '.join(words)
    
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
