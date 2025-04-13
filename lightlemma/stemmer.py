"""
Porter Stemmer implementation.
"""
from typing import Set

# Vowels and consonants
VOWELS = set('aeiou')
DOUBLE_CONSONANTS = {'bb', 'dd', 'ff', 'gg', 'mm', 'nn', 'pp', 'rr', 'tt'}

def _is_vowel(char: str, word: str, index: int) -> bool:
    """Check if a character at the given index is a vowel."""
    if char.lower() in VOWELS:
        return True
    if char.lower() == 'y':
        # If y is preceded by a vowel, it's a consonant; otherwise it's a vowel
        if index == 0:
            return True
        return not _is_vowel(word[index - 1], word, index - 1)
    return False

def _count_vc(word: str) -> int:
    """Count the number of vowel-consonant sequences."""
    count = 0
    is_prev_vowel = False
    
    for i, char in enumerate(word):
        is_vowel = _is_vowel(char, word, i)
        if not is_vowel and is_prev_vowel:
            count += 1
        is_prev_vowel = is_vowel
    
    return count

def _ends_cvc(word: str) -> bool:
    """Check if word ends in consonant-vowel-consonant sequence."""
    if len(word) < 3:
        return False
    if not _is_vowel(word[-1], word, len(word)-1) and \
       _is_vowel(word[-2], word, len(word)-2) and \
       not _is_vowel(word[-3], word, len(word)-3):
        # Special case: Don't count 'w', 'x', or 'y' as the final consonant
        return word[-1].lower() not in {'w', 'x', 'y'}
    return False

def _ends_double_consonant(word: str) -> bool:
    """Check if word ends in double consonant."""
    if len(word) < 2:
        return False
    return word[-2:].lower() in DOUBLE_CONSONANTS

def _step1a(word: str) -> str:
    """Step 1a of the Porter Stemming Algorithm."""
    if word.endswith('sses'):
        return word[:-2]
    if word.endswith('ies'):
        return word[:-2]
    if word.endswith('ss'):
        return word
    if word.endswith('s'):
        return word[:-1]
    return word

def _step1b(word: str) -> str:
    """Step 1b of the Porter Stemming Algorithm."""
    if word.endswith('eed'):
        if _count_vc(word[:-3]) > 0:
            return word[:-1]
        return word
    
    if word.endswith('ed'):
        stem = word[:-2]
        if any(_is_vowel(char, word, i) for i, char in enumerate(stem)):
            word = stem
            if word.endswith('at') or word.endswith('bl') or word.endswith('iz'):
                return word + 'e'
            if _ends_double_consonant(word) and not word.endswith(('l', 's', 'z')):
                return word[:-1]
            if _count_vc(word) == 1 and _ends_cvc(word):
                return word + 'e'
            return word
        return word
    
    if word.endswith('ing'):
        stem = word[:-3]
        if any(_is_vowel(char, word, i) for i, char in enumerate(stem)):
            word = stem
            if word.endswith('at') or word.endswith('bl') or word.endswith('iz'):
                return word + 'e'
            if _ends_double_consonant(word) and not word.endswith(('l', 's', 'z')):
                return word[:-1]
            if _count_vc(word) == 1 and _ends_cvc(word):
                return word + 'e'
            return word
        return word
    
    return word

def _step1c(word: str) -> str:
    """Step 1c of the Porter Stemming Algorithm."""
    if word.endswith('y') and len(word) > 2 and \
       not _is_vowel(word[-2], word, len(word)-2):
        return word[:-1] + 'i'
    return word

def _step2(word: str) -> str:
    """Step 2 of the Porter Stemming Algorithm."""
    pairs = [
        ('ational', 'ate'), ('tional', 'tion'), ('enci', 'ence'), ('anci', 'ance'),
        ('izer', 'ize'), ('abli', 'able'), ('alli', 'al'), ('entli', 'ent'),
        ('eli', 'e'), ('ousli', 'ous'), ('ization', 'ize'), ('ation', 'ate'),
        ('ator', 'ate'), ('alism', 'al'), ('iveness', 'ive'), ('fulness', 'ful'),
        ('ousness', 'ous'), ('aliti', 'al'), ('iviti', 'ive'), ('biliti', 'ble')
    ]
    
    for suffix, replacement in pairs:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if _count_vc(stem) > 0:
                return stem + replacement
    return word

def _step3(word: str) -> str:
    """Step 3 of the Porter Stemming Algorithm."""
    pairs = [
        ('icate', 'ic'), ('ative', ''), ('alize', 'al'), ('iciti', 'ic'),
        ('ical', 'ic'), ('ful', ''), ('ness', '')
    ]
    
    for suffix, replacement in pairs:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if _count_vc(stem) > 0:
                return stem + replacement
    return word

def _step4(word: str) -> str:
    """Step 4 of the Porter Stemming Algorithm."""
    # Handle 'um' suffix separately with its own condition
    if word.endswith('um'):
        stem = word[:-2]
        if _count_vc(stem) > 0:  # Only require one vowel-consonant sequence
            return stem
    
    suffixes = [
        'al', 'ance', 'ence', 'er', 'ic', 'able', 'ible', 'ant', 'ement',
        'ment', 'ent', 'ion', 'ou', 'ism', 'ate', 'iti', 'ous', 'ive', 'ize'
    ]
    
    for suffix in suffixes:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if _count_vc(stem) > 1:
                if suffix == 'ion' and not stem.endswith(('s', 't')):
                    continue
                return stem
    return word

def _step5a(word: str) -> str:
    """Step 5a of the Porter Stemming Algorithm."""
    if word.endswith('e'):
        stem = word[:-1]
        if _count_vc(stem) > 1:
            return stem
        if _count_vc(stem) == 1 and not _ends_cvc(stem):
            return stem
    return word

def _step5b(word: str) -> str:
    """Step 5b of the Porter Stemming Algorithm."""
    if _count_vc(word) > 1 and _ends_double_consonant(word) and word.endswith('l'):
        return word[:-1]
    return word

def stem(word: str) -> str:
    """
    Apply the Porter Stemming Algorithm to a word.
    
    Args:
        word: The word to stem.
        
    Returns:
        The stemmed form of the word.
    """
    if not word:
        return word
    
    word = word.lower()
    
    if len(word) <= 2:
        return word
    
    word = _step1a(word)
    word = _step1b(word)
    word = _step1c(word)
    word = _step2(word)
    word = _step3(word)
    word = _step4(word)
    word = _step5a(word)
    word = _step5b(word)
    
    return word 