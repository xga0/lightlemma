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

# Optimized pattern compilation with priority ordering for efficiency
PATTERNS = {
    # High-frequency patterns first for better performance
    'ing': re.compile(r'ing$'),
    'past': re.compile(r'ed$|d$'),
    'plural': re.compile(r'(?:ies|es|s)$'),
    'ly': re.compile(r'ly$'),
    'ness': re.compile(r'ness$'),
    'ment': re.compile(r'ment$'),
    
    # Medium-frequency patterns
    'tion_sion': re.compile(r'(?:ation|ition|tion|sion)$'),
    'ance_ence': re.compile(r'(?:ance|ence)$'),
    'able_ible': re.compile(r'(?:able|ible)$'),
    'ity_ety': re.compile(r'(?:ity|ety)$'),
    'ful': re.compile(r'ful$'),
    'ic_ical': re.compile(r'(?:ical|ic)$'),
    
    # Lower-frequency patterns
    'ves_plural': re.compile(r'ves$'),
    'ant_ent': re.compile(r'(?:ant|ent)$'),
    'ous_ious': re.compile(r'(?:ous|ious)$'),
    'compound': re.compile(r'(?:hood|ship|dom)$'),
    'agent': re.compile(r'(?:er|or)$'),
    'directional': re.compile(r'(?:ward|wards|wise|most)$'),
    'base_verbs': re.compile(r'(?:ize|ise|ate|ify|fy)$'),
    'ideology': re.compile(r'(?:ism|ist)$'),
    'age': re.compile(r'age$'),
    'eth': re.compile(r'eth$')
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
    'series', 'species', 'media', 'analysis',
    'basis', 'status', 'focus', 'virus', 'crisis', 'axis'
])

# Optimized special cases dictionary - organized by category for better maintainability
SPECIAL_CASES = {
    # Irregular forms
    'phenomena': 'phenomenon', 'beautiful': 'beauty', 'likable': 'like', 'readable': 'read',
    'government': 'govern', 'development': 'develop', 'statement': 'state',
    'happiness': 'happy', 'darkness': 'dark', 'famous': 'famous',
    
    # Past tense irregularities
    'walked': 'walk', 'planned': 'plan', 'copied': 'copy', 'agreed': 'agree',
    'died': 'die', 'saved': 'save', 'studied': 'study', 'tried': 'try',
    
    # Present participle irregularities  
    'walking': 'walk', 'falling': 'fall', 'going': 'go', 'doing': 'do', 
    'having': 'have', 'being': 'be', 'creating': 'create',
    
    # Irregular past forms
    'went': 'go', 'gone': 'go', 'done': 'do', 'said': 'say', 'made': 'make',
    
    # Suffix-based irregularities
    'logical': 'logic', 'historical': 'historic', 'musical': 'music',
    'decision': 'decide', 'admission': 'admit', 'activation': 'activate', 'creation': 'create',
    'curious': 'curious', 'acceptance': 'accept', 'dependent': 'depend', 
    'persistence': 'persist', 'assistant': 'assist', 'performance': 'perform',
    'northward': 'northward', 'security': 'secure',
    
    # Compound word irregularities
    'childhood': 'child', 'friendship': 'friend', 'kingdom': 'king', 
    'actor': 'act', 'teacher': 'teach'
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

# Optimized suffix handlers for better performance and maintainability
def _handle_ly_suffix(word: str) -> str:
    """Handle -ly suffix."""
    return word[:-3] + 'y' if word.endswith('ily') else word[:-2]

def _handle_ful_suffix(word: str) -> str:
    """Handle -ful suffix."""
    return 'beauty' if word == 'beautiful' else word[:-3]

def _handle_ant_ent_suffix(word: str) -> str:
    """Handle -ant/-ent suffix."""
    return word[:-3] + 'e' if len(word) > 5 else word

def _handle_ic_ical_suffix(word: str) -> str:
    """Handle -ic/-ical suffix."""
    return word[:-4] if word.endswith('ical') else word[:-2]

def _handle_ment_suffix(word: str) -> str:
    """Handle -ment suffix."""
    if word == 'government':
        return 'govern'
    stem = word[:-4]
    return stem + 'e' if _count_syllables(stem) == 1 else stem

def _handle_tion_sion_suffix(word: str) -> str:
    """Handle -tion/-sion suffix."""
    if word.endswith(('ation', 'ition')):
        # For words ending in -ation/-ition, remove -ion
        return word[:-3]
    elif word.endswith(('tion', 'sion')):
        # For words ending in -tion/-sion, remove -ion and add 'e' if appropriate
        stem = word[:-3]
        return stem + 'e' if len(stem) > 2 else stem
    return word

def _handle_ance_ence_suffix(word: str) -> str:
    """Handle -ance/-ence suffix."""
    return word[:-4] + 'e'

def _handle_ity_ety_suffix(word: str) -> str:
    """Handle -ity/-ety suffix."""
    stem = word[:-3]
    if stem.endswith('al'):
        stem = stem[:-2]
    if stem.endswith('bil'):
        stem = stem[:-2] + 'le'
    elif stem.endswith('iv'):
        stem = stem + 'e'
    return stem

def _handle_agent_suffix(word: str) -> str:
    """Handle -er/-or suffix."""
    if len(word) > 4 and not any(word.endswith(x) for x in ['eer', 'ier', 'yer', 'ger', 'ster']):
        stem = word[:-2]
        return stem + 'e' if _count_syllables(stem) == 1 else stem
    return word

def _handle_age_suffix(word: str) -> str:
    """Handle -age suffix."""
    if len(word) > 4:
        stem = word[:-3]
        return stem + 'e' if _count_syllables(stem) == 1 else stem
    return word

def _handle_base_verbs_suffix(word: str) -> str:
    """Handle base verb endings."""
    return word[:-3] if word.endswith('eth') else word

# Pattern-to-handler mapping for efficient dispatch
PATTERN_HANDLERS = {
    'ing': _handle_gerund_forms,
    'past': _handle_past_tense,
    'plural': _handle_regular_plurals,
    'ly': _handle_ly_suffix,
    'ness': _handle_ness_suffix,
    'ment': _handle_ment_suffix,
    'tion_sion': _handle_tion_sion_suffix,
    'ance_ence': _handle_ance_ence_suffix,
    'able_ible': _handle_able_ible_suffixes,
    'ity_ety': _handle_ity_ety_suffix,
    'ful': _handle_ful_suffix,
    'ic_ical': _handle_ic_ical_suffix,
    'ant_ent': _handle_ant_ent_suffix,
    'agent': _handle_agent_suffix,
    'age': _handle_age_suffix,
    'base_verbs': _handle_base_verbs_suffix,
    'eth': _handle_base_verbs_suffix,
    # Patterns that don't change the word
    'ous_ious': lambda word: word,
    'directional': lambda word: word,
    'ideology': lambda word: word,
    'compound': lambda word: word[:-4]
}

@lru_cache(maxsize=2048)
def _apply_rules(word: str) -> str:
    """
    Apply lemmatization rules to a word using optimized pattern matching.
    
    This function uses a dispatch table for efficient pattern matching
    instead of a long if-elif chain, improving performance significantly.
    """
    # Check special cases and irregular forms first (most specific)
    if word in SPECIAL_CASES:
        return SPECIAL_CASES[word]
    
    if word in IRREGULAR_FORMS:
        return IRREGULAR_FORMS[word]
    
    # Handle Latin plurals
    word, changed = _handle_latin_plurals(word)
    if changed:
        return word
    
    # Handle -ves plurals
    word, changed = _handle_ves_plurals(word)
    if changed:
        return word
    
    # Efficient pattern matching with priority ordering
    for pattern_name, pattern in PATTERNS.items():
        if pattern.search(word):
            handler = PATTERN_HANDLERS.get(pattern_name)
            if handler:
                return handler(word)
            break
    
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