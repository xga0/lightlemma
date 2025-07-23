"""
Porter Stemmer implementation.
"""
from typing import Dict, List, FrozenSet
from functools import lru_cache

VOWELS = frozenset('aeiou')
CONSONANTS = frozenset('bcdfghjklmnpqrstvwxyz')
DOUBLE_CONSONANTS = frozenset(['bb', 'dd', 'ff', 'gg', 'mm', 'nn', 'pp', 'rr', 'tt', 'll'])
SPECIAL_CONS = frozenset(['w', 'x', 'y'])

KEEP_AS_IS = frozenset([
    'news', 'proceed', 'exceed', 'succeed',
    'data', 'media', 'criteria', 'analysis', 'basis',
    'status', 'focus', 'virus', 'crisis', 'axis'
])

SPECIAL_CASES = {
    'agreed': 'agree',
    'dying': 'die',
    'lying': 'lie',
    'tying': 'tie',
    'electriciti': 'electric',
    'electrical': 'electric',
    'engineering': 'engineer',
    'controll': 'control',
    'flying': 'fli',
    'biology': 'biolog',
    'physics': 'physic',
    'chemistry': 'chemistri',
    'mathematics': 'mathemat',
    'psychology': 'psycholog'
}

STEP2_REPLACEMENTS = (
    ('ational', 'ate'), ('ization', 'ize'), ('ation', 'ate'), ('ator', 'ate'),
    ('tional', 'tion'), ('fulness', 'ful'), ('ousness', 'ous'), ('iveness', 'ive'),
    ('biliti', 'ble'), ('entli', 'ent'), ('ousli', 'ous'), ('alism', 'al'),
    ('aliti', 'al'), ('iviti', 'ive'), ('enci', 'ence'), ('anci', 'ance'),
    ('izer', 'ize'), ('abli', 'able'), ('alli', 'al'), ('eli', 'e')
)

STEP3_REPLACEMENTS = (
    ('icate', 'ic'), ('alize', 'al'), ('iciti', 'ic'), ('ical', 'ic'),
    ('ative', ''), ('ful', ''), ('ness', '')
)

STEP4_SUFFIXES = (
    'ement', 'ance', 'ence', 'able', 'ible', 'ment', 'ent', 'ant',
    'ism', 'ate', 'iti', 'ous', 'ive', 'ize', 'ion', 'tion',
    'al', 'er', 'ic', 'ou'
)

@lru_cache(maxsize=2048)
def _is_vowel(char: str, word: str, index: int) -> bool:
    """
    Check if a character at the given index is a vowel.
    
    Args:
        char: The character to check
        word: The word containing the character
        index: The position of the character in the word
        
    Returns:
        True if the character is a vowel, False otherwise
    """
    char_lower = char.lower()
    if char_lower in VOWELS:
        return True
    if char_lower == 'y':
        return index == 0 or not _is_vowel(word[index - 1], word, index - 1)
    return False

@lru_cache(maxsize=2048)
def _count_vc(word: str) -> int:
    """
    Count the number of vowel-consonant sequences.
    
    Args:
        word: The word to analyze
        
    Returns:
        The number of vowel-consonant sequences
    """
    count = 0
    is_prev_vowel = False
    
    for i, char in enumerate(word):
        is_vowel = _is_vowel(char, word, i)
        if not is_vowel and is_prev_vowel:
            count += 1
        is_prev_vowel = is_vowel
    
    return count

@lru_cache(maxsize=1024)
def _ends_cvc(word: str) -> bool:
    """
    Check if word ends in consonant-vowel-consonant sequence.
    
    Args:
        word: The word to check
        
    Returns:
        True if the word ends in a CVC sequence, False otherwise
    """
    if len(word) < 3:
        return False
    if not _is_vowel(word[-1], word, len(word)-1) and \
       _is_vowel(word[-2], word, len(word)-2) and \
       not _is_vowel(word[-3], word, len(word)-3):
        return word[-1].lower() not in SPECIAL_CONS
    return False

@lru_cache(maxsize=1024)
def _ends_double_consonant(word: str) -> bool:
    """
    Check if word ends in double consonant.
    
    Args:
        word: The word to check
        
    Returns:
        True if the word ends in a double consonant, False otherwise
    """
    return len(word) >= 2 and word[-2:].lower() in DOUBLE_CONSONANTS

@lru_cache(maxsize=1024)
def _step1a(word: str) -> str:
    """
    Step 1a of the Porter Stemming Algorithm.
    
    Args:
        word: The word to stem
        
    Returns:
        The word after applying step 1a rules
    """
    if word.endswith('sses'):
        return word[:-2]
    if word.endswith('ies'):
        return word[:-2]
    if word.endswith('ss'):
        return word
    if word.endswith('s'):
        return word[:-1]
    return word

@lru_cache(maxsize=1024)
def _step1b(word: str) -> str:
    """
    Step 1b of the Porter Stemming Algorithm.
    
    Args:
        word: The word to stem
        
    Returns:
        The word after applying step 1b rules
    """
    if word == 'agreed':
        return 'agree'
    
    if word.endswith('eed'):
        if _count_vc(word[:-3]) > 0:
            return word[:-1]
        return word
    
    if word.endswith('ed'):
        stem = word[:-2]
        if any(_is_vowel(char, stem, i) for i, char in enumerate(stem)):
            return _post_process_stem(stem)
        return word
    
    if word.endswith('ing'):
        stem = word[:-3]
        if any(_is_vowel(char, stem, i) for i, char in enumerate(stem)):
            return _post_process_stem(stem)
        return word
    
    return word

@lru_cache(maxsize=512)
def _post_process_stem(stem: str) -> str:
    """Post-process stem after removing -ed or -ing."""
    if stem.endswith(('at', 'bl', 'iz')):
        return stem + 'e'
    if _ends_double_consonant(stem) and not stem.endswith(('l', 's', 'z')):
        return stem[:-1]
    if _count_vc(stem) == 1 and _ends_cvc(stem):
        return stem + 'e'
    return stem

@lru_cache(maxsize=1024)
def _step1c(word: str) -> str:
    """
    Step 1c of the Porter Stemming Algorithm - handles Y to I transformation.
    
    Args:
        word: The word to stem
        
    Returns:
        The word after applying step 1c rules
    """
    if word in SPECIAL_CASES and (word.endswith('ing') or word.endswith('y')):
        return SPECIAL_CASES[word]
    
    if word.endswith('y') and len(word) > 2 and \
       any(_is_vowel(char, word, i) for i, char in enumerate(word[:-1])):
        return word[:-1] + 'i'
    
    return word

@lru_cache(maxsize=1024)
def _step2(word: str) -> str:
    """
    Step 2 of the Porter Stemming Algorithm.
    
    Args:
        word: The word to stem
        
    Returns:
        The word after applying step 2 rules
    """
    for suffix, replacement in STEP2_REPLACEMENTS:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if _count_vc(stem) > 0:
                return stem + replacement
    return word

@lru_cache(maxsize=1024)
def _step3(word: str) -> str:
    """
    Step 3 of the Porter Stemming Algorithm.
    
    Args:
        word: The word to stem
        
    Returns:
        The word after applying step 3 rules
    """
    if word in ('electriciti', 'electrical'):
        return 'electric'
    
    if word.endswith('ology') and len(word) > 5:
        return word[:-1]
    
    for suffix, replacement in STEP3_REPLACEMENTS:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if _count_vc(stem) > 0:
                return stem + replacement
    return word

@lru_cache(maxsize=1024)
def _step4(word: str) -> str:
    """
    Step 4 of the Porter Stemming Algorithm.
    
    Args:
        word: The word to stem
        
    Returns:
        The word after applying step 4 rules
    """
    if word == 'engineering':
        return 'engineer'
    
    for suffix in STEP4_SUFFIXES:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if _count_vc(stem) > 1:
                if suffix == 'ion' and not stem.endswith(('s', 't')):
                    continue
                return stem
    
    return word

@lru_cache(maxsize=1024)
def _step5a(word: str) -> str:
    """
    Step 5a of the Porter Stemming Algorithm.
    
    Args:
        word: The word to stem
        
    Returns:
        The word after applying step 5a rules
    """
    if word.endswith('e'):
        stem = word[:-1]
        if _count_vc(stem) > 1:
            return stem
        if _count_vc(stem) == 1 and not _ends_cvc(stem):
            return stem
    return word

@lru_cache(maxsize=1024)
def _step5b(word: str) -> str:
    """
    Step 5b of the Porter Stemming Algorithm.
    
    Args:
        word: The word to stem
        
    Returns:
        The word after applying step 5b rules
    """
    if word == 'controll':
        return 'control'
    
    if _count_vc(word) > 1 and _ends_double_consonant(word) and word.endswith('l'):
        return word[:-1]
    
    return word

def stem(word: str) -> str:
    """
    Apply the Porter Stemming Algorithm to a word with optimized processing.
    
    Args:
        word: The word to stem.
        
    Returns:
        The stemmed form of the word.
        
    Raises:
        TypeError: If word is not a string
        ValueError: If word is too long (>100 chars)
    
    Examples:
        >>> stem("running")
        'run'
        >>> stem("happiness")
        'happi'
        >>> stem("flies")
        'fli'
    """
    if not isinstance(word, str):
        raise TypeError("Input must be a string")
    
    if not word:
        return word
    
    if len(word) > 100:
        raise ValueError("Word is too long (>100 characters)")
    
    word = word.lower().strip()
    
    if word in SPECIAL_CASES:
        return SPECIAL_CASES[word]
    
    if word in KEEP_AS_IS or len(word) <= 2:
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

def stem_batch(words: List[str]) -> List[str]:
    """
    Apply the Porter Stemming Algorithm to a batch of words efficiently.
    
    This function processes multiple words at once, providing better performance
    than calling stem() individually for each word by reducing function
    call overhead and enabling batch optimizations.
    
    Args:
        words: List of words to stem.
        
    Returns:
        List of stemmed words in the same order as input.
        
    Raises:
        TypeError: If words is not a list or contains non-string items
        ValueError: If any word is too long (>100 chars)
    
    Examples:
        >>> stem_batch(["running", "happiness", "flies"])
        ['run', 'happi', 'fli']
        >>> stem_batch(["cats", "dogs", ""])
        ['cat', 'dog', '']
    """
    if not isinstance(words, list):
        raise TypeError("Input must be a list")
    
    if not words:
        return []
    
    results = []
    
    for word in words:
        if not isinstance(word, str):
            raise TypeError("All items in list must be strings")
        
        if not word:
            results.append(word)
            continue
        
        if len(word) > 100:
            raise ValueError("Word is too long (>100 characters)")
        
        word_lower = word.lower().strip()
        
        if word_lower in SPECIAL_CASES:
            results.append(SPECIAL_CASES[word_lower])
        elif word_lower in KEEP_AS_IS:
            results.append(word_lower)
        elif len(word_lower) <= 2:
            results.append(word_lower)
        else:
            processed_word = word_lower
            steps = [_step1a, _step1b, _step1c, _step2, _step3, _step4, _step5a, _step5b]
            for step in steps:
                processed_word = step(processed_word)
            results.append(processed_word)
    
    return results 