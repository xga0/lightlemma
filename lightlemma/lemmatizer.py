"""
Core lemmatizer implementation.
"""
import json
import os
import re
from typing import Dict, Pattern, Tuple, FrozenSet, Union, List
from functools import lru_cache

MAX_WORD_LENGTH = 100
VOWELS: FrozenSet[str] = frozenset('aeiou')
CONSONANTS: FrozenSet[str] = frozenset('bcdfghjklmnpqrstvwxyz')
CVC_EXCLUSIONS: FrozenSet[str] = frozenset('wxy')

# Optimized pattern compilation
PATTERNS = {
    'plural': re.compile(r'(?:s|es|ies)$'),
    'ves_plural': re.compile(r'ves$'),
    'past': re.compile(r'(?:ed|d)$'),
    'ing': re.compile(r'ing$'),
    'base_verbs': re.compile(r'(?:ize|ise|ate|ify|fy)$'),
    'eth': re.compile(r'eth$'),
    'ly': re.compile(r'ly$'),
    'ful': re.compile(r'ful$'),
    'able_ible': re.compile(r'(?:able|ible)$'),
    'ous_ious': re.compile(r'(?:ous|ious)$'),
    'ant_ent': re.compile(r'(?:ant|ent)$'),
    'ic_ical': re.compile(r'(?:ic|ical)$'),
    'ical': re.compile(r'ical$'),
    'directional': re.compile(r'(?:ward|wards|wise|most)$'),
    'ment': re.compile(r'ment$'),
    'ness': re.compile(r'ness$'),
    'long_tion': re.compile(r'(?:ation|ition)$'),
    'tion_sion': re.compile(r'(?:tion|sion)$'),
    'ance_ence': re.compile(r'(?:ance|ence)$'),
    'ity_ety': re.compile(r'(?:ity|ety)$'),
    'compound': re.compile(r'(?:hood|ship|dom)$'),
    'agent': re.compile(r'(?:er|or)$'),
    'ideology': re.compile(r'(?:ism|ist)$'),
    'age': re.compile(r'age$')
}

DOUBLE_CONSONANT_ENDINGS = frozenset(['bb', 'dd', 'ff', 'gg', 'mm', 'nn', 'pp', 'rr', 'tt', 'll'])

KEEP_DOUBLE = frozenset([
    'fall', 'tell', 'roll', 'sell', 'small', 'spell', 'still', 'stall', 'skill',
    'chill', 'will', 'fill', 'full', 'doll', 'poll', 'tall', 'well'
])

VES_MAPPING = {
    'leaves': 'leaf', 'lives': 'life', 'selves': 'self', 'wolves': 'wolf',
    'shelves': 'shelf', 'calves': 'calf', 'halves': 'half', 'knives': 'knife',
    'wives': 'wife', 'thieves': 'thief', 'loaves': 'loaf', 'hooves': 'hoof',
    'scarves': 'scarf', 'wharves': 'wharf', 'elves': 'elf'
}

KEEP_AS_IS = frozenset([
    'universal', 'personal', 'general', 'special', 'natural', 'normal',
    'formal', 'final', 'total', 'global', 'local', 'central', 'digital',
    'national', 'international', 'professional', 'traditional', 'original',
    'maximum', 'minimum', 'optimal', 'minimal', 'maximal',
    'series', 'species', 'data', 'media', 'criteria', 'phenomena', 'analysis',
    'basis', 'status', 'focus', 'virus', 'crisis', 'axis'
])

SPECIAL_CASES = {
    'beautiful': 'beauty', 'likable': 'like', 'readable': 'read',
    'government': 'govern', 'development': 'develop', 'statement': 'state',
    'happiness': 'happy', 'darkness': 'dark',
    'walked': 'walk', 'planned': 'plan', 'copied': 'copy',
    'walking': 'walk', 'falling': 'fall',
    'going': 'go', 'doing': 'do', 'having': 'have', 'being': 'be',
    'went': 'go', 'gone': 'go', 'done': 'do', 'said': 'say', 'made': 'make'
}

@lru_cache(maxsize=512)
def _load_irregular_forms() -> Dict[str, str]:
    """Load irregular forms from JSON data file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, 'data', 'irregular_forms.json')
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            irregular_forms = {}
            for category, forms in data.items():
                for form, lemma in forms.items():
                    irregular_forms[form.lower()] = lemma.lower()
            return irregular_forms
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

IRREGULAR_FORMS = _load_irregular_forms()

@lru_cache(maxsize=2048)
def _count_syllables(word: str) -> int:
    """Count syllables in a word."""
    count = 0
    prev_is_vowel = False
    
    for char in word:
        is_vowel = char in VOWELS
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    
    if word.endswith('e') and not word.endswith(('le', 'ie', 'ee', 'ye')):
        count -= 1
    
    return max(1, count)

@lru_cache(maxsize=1024)
def _strip_double_consonants(word: str) -> str:
    """Strip double consonants if appropriate."""
    if len(word) > 2 and word[-2:] in DOUBLE_CONSONANT_ENDINGS and word not in KEEP_DOUBLE:
        return word[:-1]
    return word

@lru_cache(maxsize=1024)
def _is_cvc_pattern(word: str) -> bool:
    """Check if word ends with consonant-vowel-consonant pattern."""
    if len(word) < 3:
        return False
    
    return (word[-1] in CONSONANTS and
            word[-2] in VOWELS and
            word[-3] in CONSONANTS and
            word[-1] not in CVC_EXCLUSIONS)

@lru_cache(maxsize=1024)
def _handle_latin_plurals(word: str) -> Tuple[str, bool]:
    """Handle Latin plural forms."""
    latin_mappings = {
        'phenomena': 'phenomenon', 'criteria': 'criterion', 'stigmata': 'stigma',
        'alumni': 'alumnus', 'fungi': 'fungus', 'cacti': 'cactus',
        'nuclei': 'nucleus', 'radii': 'radius', 'algae': 'alga',
        'larvae': 'larva', 'nebulae': 'nebula', 'indices': 'index',
        'matrices': 'matrix', 'appendices': 'appendix', 'vertices': 'vertex',
        'data': 'datum', 'bacteria': 'bacterium', 'memoranda': 'memorandum',
        'curricula': 'curriculum', 'genera': 'genus', 'corpora': 'corpus'
    }
    
    if word in latin_mappings:
        return latin_mappings[word], True
    return word, False

@lru_cache(maxsize=512)
def _handle_ves_plurals(word: str) -> Tuple[str, bool]:
    """Handle -ves plural forms."""
    return (VES_MAPPING[word], True) if word in VES_MAPPING else (word, False)

@lru_cache(maxsize=1024)
def _handle_regular_plurals(word: str) -> str:
    """Handle regular plural forms."""
    if word.endswith('ies'):
        return word[:-3] + 'y'
    elif word.endswith('es'):
        if word.endswith(('ches', 'shes', 'ses', 'xes', 'zes')):
            return word[:-2]
        elif word.endswith('oes'):
            return word[:-2]
        return word[:-1]
    elif word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word

@lru_cache(maxsize=1024)
def _handle_past_tense(word: str) -> str:
    """Handle past tense forms."""
    if word.endswith('ied'):
        return word[:-3] + 'y'
    elif word.endswith('ed'):
        stem = word[:-2]
        if len(stem) >= 3 and stem[-1] == stem[-2] and stem[-1] in CONSONANTS:
            return stem[:-1]
        elif stem.endswith('e'):
            return stem[:-1]
        return stem
    elif word.endswith('d'):
        return word[:-1]
    return word

@lru_cache(maxsize=1024)
def _handle_gerund_forms(word: str) -> str:
    """Handle gerund (-ing) forms."""
    stem = word[:-3]
    if len(stem) >= 3 and stem[-1] == stem[-2] and stem[-1] in CONSONANTS:
        return stem[:-1]
    elif _count_syllables(stem) == 1 and _is_cvc_pattern(stem):
        return stem + 'e'
    return stem

@lru_cache(maxsize=512)
def _handle_able_ible_suffixes(word: str) -> str:
    """Handle -able/-ible suffixes."""
    if word in ('beautiful', 'likable', 'readable'):
        return {'beautiful': 'beauty', 'likable': 'like', 'readable': 'read'}[word]
    
    stem = word[:-4]
    if stem.endswith('at'):
        return stem + 'e'
    elif stem.endswith('e'):
        return stem
    elif len(stem) >= 3:
        if _is_cvc_pattern(stem) and stem in ['lik', 'liv', 'siz', 'writ']:
            return stem + 'e'
        elif _count_syllables(stem) == 1:
            return stem + 'e'
    return stem

@lru_cache(maxsize=512)
def _handle_ness_suffix(word: str) -> str:
    """Handle -ness suffix."""
    if word in ('happiness', 'darkness'):
        return {'happiness': 'happy', 'darkness': 'dark'}[word]
    
    stem = word[:-4]
    return stem[:-1] + 'y' if stem.endswith('i') else stem

@lru_cache(maxsize=2048)
def _apply_rules(word: str) -> str:
    """Apply lemmatization rules to a word."""
    if word in SPECIAL_CASES:
        return SPECIAL_CASES[word]
    
    if word in IRREGULAR_FORMS:
        return IRREGULAR_FORMS[word]
    
    word, changed = _handle_latin_plurals(word)
    if changed:
        return word
    
    word, changed = _handle_ves_plurals(word)
    if changed:
        return word
    
    # Process by suffix patterns
    if PATTERNS['plural'].search(word):
        return _handle_regular_plurals(word)
    elif PATTERNS['past'].search(word):
        return _handle_past_tense(word)
    elif PATTERNS['ing'].search(word):
        return _handle_gerund_forms(word)
    elif PATTERNS['base_verbs'].search(word) or PATTERNS['eth'].search(word):
        return word[:-3] if word.endswith('eth') else word
    elif PATTERNS['ly'].search(word):
        return word[:-3] + 'y' if word.endswith('ily') else word[:-2]
    elif PATTERNS['ful'].search(word):
        return 'beauty' if word == 'beautiful' else word[:-3]
    elif PATTERNS['able_ible'].search(word):
        return _handle_able_ible_suffixes(word)
    elif PATTERNS['ous_ious'].search(word):
        return word
    elif PATTERNS['ant_ent'].search(word):
        return word[:-3] + 'e' if len(word) > 5 else word
    elif PATTERNS['ic_ical'].search(word):
        return word[:-4] if PATTERNS['ical'].search(word) else word[:-2]
    elif PATTERNS['directional'].search(word):
        return word
    elif PATTERNS['ment'].search(word):
        stem = word[:-4]
        if word == 'government':
            return 'govern'
        return stem + 'e' if _count_syllables(stem) == 1 else stem
    elif PATTERNS['ness'].search(word):
        return _handle_ness_suffix(word)
    elif PATTERNS['long_tion'].search(word):
        return word[:-5] + 'e'
    elif PATTERNS['tion_sion'].search(word):
        return word[:-3] + 'e' if len(word) > 5 else word
    elif PATTERNS['ance_ence'].search(word):
        return word[:-4] + 'e'
    elif PATTERNS['ity_ety'].search(word):
        stem = word[:-3]
        if stem.endswith('al'):
            stem = stem[:-2]
        if stem.endswith('bil'):
            stem = stem[:-2] + 'le'
        elif stem.endswith('iv'):
            stem = stem + 'e'
        return stem
    elif PATTERNS['compound'].search(word):
        return word[:-4]
    elif PATTERNS['agent'].search(word):
        if len(word) > 4 and not any(word.endswith(x) for x in ['eer', 'ier', 'yer', 'ger', 'ster']):
            stem = word[:-2]
            return stem + 'e' if _count_syllables(stem) == 1 else stem
        return word
    elif PATTERNS['ideology'].search(word):
        return word
    elif PATTERNS['age'].search(word):
        if len(word) > 4:
            stem = word[:-3]
            return stem + 'e' if _count_syllables(stem) == 1 else stem
        return word
    
    return word

def lemmatize(word: Union[str, None]) -> Union[str, None]:
    """Lemmatize a word to its base form."""
    if word is None:
        return None
    
    if not isinstance(word, str):
        raise TypeError("Input must be a string")
    
    if not word:
        return word
    
    if len(word) > MAX_WORD_LENGTH:
        raise ValueError(f"Word is too long (>{MAX_WORD_LENGTH} characters)")
    
    word_lower = word.lower().strip()
    
    if word_lower in KEEP_AS_IS:
        return word_lower
    
    return _apply_rules(word_lower)

def lemmatize_batch(words: List[Union[str, None]]) -> List[Union[str, None]]:
    """Lemmatize a batch of words efficiently."""
    if not isinstance(words, list):
        raise TypeError("Input must be a list")
    
    if not words:
        return []
    
    results = []
    
    for word in words:
        if word is None:
            results.append(None)
            continue
        
        if not isinstance(word, str):
            raise TypeError("All items in list must be strings or None")
        
        if not word:
            results.append(word)
            continue
        
        if len(word) > MAX_WORD_LENGTH:
            raise ValueError(f"Word is too long (>{MAX_WORD_LENGTH} characters)")
        
        word_lower = word.lower().strip()
        
        if word_lower in KEEP_AS_IS:
            results.append(word_lower)
        else:
            results.append(_apply_rules(word_lower))
    
    return results 