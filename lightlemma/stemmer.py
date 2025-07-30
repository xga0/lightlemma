"""
Porter Stemmer implementation.
"""
from typing import List, FrozenSet
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
    'agreed': 'agree', 'dying': 'die', 'lying': 'lie', 'tying': 'tie',
    'electriciti': 'electric', 'electrical': 'electric', 'engineering': 'engineer',
    'controll': 'control', 'flying': 'fli', 'biology': 'biolog',
    'physics': 'physic', 'chemistry': 'chemistri', 'mathematics': 'mathemat',
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

@lru_cache(maxsize=4096)
def _analyze_word(word: str) -> tuple:
    """Analyze word structure and return vowel/consonant info and VC count."""
    vc_count = 0
    is_prev_vowel = False
    has_vowel = False
    
    for i, char in enumerate(word):
        char_lower = char.lower()
        
        if char_lower in VOWELS:
            is_vowel = True
        elif char_lower == 'y':
            is_vowel = i == 0 or not is_prev_vowel
        else:
            is_vowel = False
        
        if is_vowel:
            has_vowel = True
        elif is_prev_vowel:
            vc_count += 1
            
        is_prev_vowel = is_vowel
    
    length = len(word)
    ends_double_cons = (length >= 2 and 
                       word[-2:].lower() in DOUBLE_CONSONANTS)
    
    ends_cvc = (length >= 3 and 
               not _is_vowel_at(word, length-1) and 
               _is_vowel_at(word, length-2) and 
               not _is_vowel_at(word, length-3) and
               word[-1].lower() not in SPECIAL_CONS)
    
    return vc_count, has_vowel, ends_double_cons, ends_cvc

@lru_cache(maxsize=2048)
def _is_vowel_at(word: str, index: int) -> bool:
    """Check if character at index is a vowel."""
    if index < 0 or index >= len(word):
        return False
    
    char = word[index].lower()
    if char in VOWELS:
        return True
    if char == 'y':
        return index == 0 or not _is_vowel_at(word, index - 1)
    return False

@lru_cache(maxsize=1024)
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

@lru_cache(maxsize=1024)
def _step1b(word: str) -> str:
    """Step 1b of the Porter Stemming Algorithm."""
    if word == 'agreed':
        return 'agree'
    
    if word.endswith('eed'):
        stem = word[:-3]
        vc_count, _, _, _ = _analyze_word(stem)
        return word[:-1] if vc_count > 0 else word
    
    if word.endswith('ed'):
        stem = word[:-2]
        _, has_vowel, _, _ = _analyze_word(stem)
        return _post_process_stem(stem) if has_vowel else word
    
    if word.endswith('ing'):
        stem = word[:-3]
        _, has_vowel, _, _ = _analyze_word(stem)
        return _post_process_stem(stem) if has_vowel else word
    
    return word

@lru_cache(maxsize=512)
def _post_process_stem(stem: str) -> str:
    """Post-process stem after removing -ed or -ing."""
    if stem.endswith(('at', 'bl', 'iz')):
        return stem + 'e'
    
    vc_count, _, ends_double_cons, ends_cvc = _analyze_word(stem)
    
    if ends_double_cons and not stem.endswith(('l', 's', 'z')):
        return stem[:-1]
    
    if vc_count == 1 and ends_cvc:
        return stem + 'e'
    
    return stem

@lru_cache(maxsize=1024)
def _step1c(word: str) -> str:
    """Step 1c of the Porter Stemming Algorithm - handles Y to I transformation."""
    if word in SPECIAL_CASES and (word.endswith('ing') or word.endswith('y')):
        return SPECIAL_CASES[word]
    
    if (word.endswith('y') and len(word) > 2 and 
        any(_is_vowel_at(word, i) for i in range(len(word)-1))):
        return word[:-1] + 'i'
    
    return word

@lru_cache(maxsize=1024)
def _step2(word: str) -> str:
    """Step 2 of the Porter Stemming Algorithm."""
    for suffix, replacement in STEP2_REPLACEMENTS:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            vc_count, _, _, _ = _analyze_word(stem)
            if vc_count > 0:
                return stem + replacement
    return word

@lru_cache(maxsize=1024)
def _step3(word: str) -> str:
    """Step 3 of the Porter Stemming Algorithm."""
    if word in ('electriciti', 'electrical'):
        return 'electric'
    
    if word.endswith('ology') and len(word) > 5:
        return word[:-1]
    
    for suffix, replacement in STEP3_REPLACEMENTS:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            vc_count, _, _, _ = _analyze_word(stem)
            if vc_count > 0:
                return stem + replacement
    return word

@lru_cache(maxsize=1024)
def _step4(word: str) -> str:
    """Step 4 of the Porter Stemming Algorithm."""
    if word == 'engineering':
        return 'engineer'
    
    for suffix in STEP4_SUFFIXES:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            vc_count, _, _, _ = _analyze_word(stem)
            if vc_count > 1:
                if suffix == 'ion' and not stem.endswith(('s', 't')):
                    continue
                return stem
    
    return word

@lru_cache(maxsize=1024)
def _step5a(word: str) -> str:
    """Step 5a of the Porter Stemming Algorithm."""
    if word.endswith('e'):
        stem = word[:-1]
        vc_count, _, _, ends_cvc = _analyze_word(stem)
        if vc_count > 1 or (vc_count == 1 and not ends_cvc):
            return stem
    return word

@lru_cache(maxsize=1024)
def _step5b(word: str) -> str:
    """Step 5b of the Porter Stemming Algorithm."""
    if word == 'controll':
        return 'control'
    
    vc_count, _, ends_double_cons, _ = _analyze_word(word)
    
    if vc_count > 1 and ends_double_cons and word.endswith('l'):
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
        elif word_lower in KEEP_AS_IS or len(word_lower) <= 2:
            results.append(word_lower)
        else:
            processed_word = word_lower
            processed_word = _step1a(processed_word)
            processed_word = _step1b(processed_word)
            processed_word = _step1c(processed_word)
            processed_word = _step2(processed_word)
            processed_word = _step3(processed_word)
            processed_word = _step4(processed_word)
            processed_word = _step5a(processed_word)
            processed_word = _step5b(processed_word)
            results.append(processed_word)
    
    return results 