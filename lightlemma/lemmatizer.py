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

PATTERNS = {
    'ing': re.compile(r'ing$'),
    'past': re.compile(r'ed$|d$'),
    'plural': re.compile(r'(?:ies|es|s)$'),
    'ly': re.compile(r'ly$'),
    'ness': re.compile(r'ness$'),
    'ment': re.compile(r'ment$'),
    'tion_sion': re.compile(r'(?:ation|ition|tion|sion)$'),
    'ance_ence': re.compile(r'(?:ance|ence)$'),
    'able_ible': re.compile(r'(?:able|ible)$'),
    'ity_ety': re.compile(r'(?:ity|ety)$'),
    'ful': re.compile(r'ful$'),
    'ic_ical': re.compile(r'(?:ical|ic)$'),
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

SPECIAL_CASES = {
    'phenomena': 'phenomenon', 'beautiful': 'beauty', 'likable': 'like', 'readable': 'read',
    'government': 'govern', 'development': 'develop', 'statement': 'state',
    'happiness': 'happy', 'darkness': 'dark', 'famous': 'famous',
    'walked': 'walk', 'planned': 'plan', 'copied': 'copy', 'agreed': 'agree',
    'died': 'die', 'saved': 'save', 'studied': 'study', 'tried': 'try',
    'walking': 'walk', 'falling': 'fall', 'going': 'go', 'doing': 'do', 
    'having': 'have', 'being': 'be', 'creating': 'create',
    'went': 'go', 'gone': 'go', 'done': 'do', 'said': 'say', 'made': 'make',
    'logical': 'logic', 'historical': 'historic', 'musical': 'music',
    'decision': 'decide', 'admission': 'admit', 'activation': 'activate', 'creation': 'create',
    'curious': 'curious', 'acceptance': 'accept', 'dependent': 'depend', 
    'persistence': 'persist', 'assistant': 'assist', 'performance': 'perform',
    'northward': 'northward', 'security': 'secure',
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
            for forms in data.values():
                irregular_forms.update({form.lower(): lemma.lower() for form, lemma in forms.items()})
            return irregular_forms
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

IRREGULAR_FORMS = _load_irregular_forms()

LATIN_MAPPING = {
    'phenomena': 'phenomenon', 'criteria': 'criterion', 'stigmata': 'stigma',
    'alumni': 'alumnus', 'fungi': 'fungus', 'cacti': 'cactus',
    'nuclei': 'nucleus', 'radii': 'radius', 'algae': 'alga',
    'larvae': 'larva', 'nebulae': 'nebula', 'indices': 'index',
    'matrices': 'matrix', 'appendices': 'appendix', 'vertices': 'vertex',
    'data': 'datum', 'bacteria': 'bacterium', 'memoranda': 'memorandum',
    'curricula': 'curriculum', 'genera': 'genus', 'corpora': 'corpus'
}

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
def _is_cvc_pattern(word: str) -> bool:
    """Check if word ends with consonant-vowel-consonant pattern."""
    return (len(word) >= 3 and 
            word[-1] in CONSONANTS and
            word[-2] in VOWELS and
            word[-3] in CONSONANTS and
            word[-1] not in CVC_EXCLUSIONS)

@lru_cache(maxsize=1024)
def _handle_regular_plurals(word: str) -> str:
    """Handle regular plural forms."""
    if word.endswith('ies'):
        return word[:-3] + 'y'
    elif word.endswith('es'):
        if word.endswith(('ches', 'shes', 'ses', 'xes', 'zes', 'oes')):
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
        if (len(stem) >= 3 and stem[-1] == stem[-2] and 
            stem[-1] in CONSONANTS and stem not in KEEP_DOUBLE):
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
    if (len(stem) >= 3 and stem[-1] == stem[-2] and 
        stem[-1] in CONSONANTS and stem not in KEEP_DOUBLE):
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
        if _is_cvc_pattern(stem) and stem in ('lik', 'liv', 'siz', 'writ'):
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
    """Apply lemmatization rules to a word using optimized pattern matching."""
    
    if word in SPECIAL_CASES:
        return SPECIAL_CASES[word]
    
    if word in IRREGULAR_FORMS:
        return IRREGULAR_FORMS[word]
    
    if word in LATIN_MAPPING:
        return LATIN_MAPPING[word]
    
    if word in VES_MAPPING:
        return VES_MAPPING[word]
    
    if word.endswith('ing'):
        return _handle_gerund_forms(word)
    
    if word.endswith('ed') or word.endswith('d'):
        if PATTERNS['past'].search(word):
            return _handle_past_tense(word)
    
    if word.endswith(('ies', 'es', 's')):
        if PATTERNS['plural'].search(word):
            return _handle_regular_plurals(word)
    
    if word.endswith('ly'):
        return word[:-3] + 'y' if word.endswith('ily') else word[:-2]
    
    if word.endswith('ness'):
        return _handle_ness_suffix(word)
    
    if word.endswith('ment'):
        if word == 'government':
            return 'govern'
        stem = word[:-4]
        return stem + 'e' if _count_syllables(stem) == 1 else stem
    
    if word.endswith(('ation', 'ition')):
        return word[:-3]
    elif word.endswith(('tion', 'sion')):
        stem = word[:-3]
        return stem + 'e' if len(stem) > 2 else stem
    
    if word.endswith(('ance', 'ence')):
        return word[:-4] + 'e'
    
    if word.endswith(('able', 'ible')):
        return _handle_able_ible_suffixes(word)
    
    if word.endswith(('ity', 'ety')):
        stem = word[:-3]
        if stem.endswith('al'):
            stem = stem[:-2]
        if stem.endswith('bil'):
            stem = stem[:-2] + 'le'
        elif stem.endswith('iv'):
            stem = stem + 'e'
        return stem
    
    if word.endswith('ful'):
        return 'beauty' if word == 'beautiful' else word[:-3]
    
    if word.endswith('ical'):
        return word[:-4]
    elif word.endswith('ic'):
        return word[:-2]
    
    if word.endswith(('ant', 'ent')):
        return word[:-3] + 'e' if len(word) > 5 else word
    
    if word.endswith(('er', 'or')):
        if (len(word) > 4 and 
            not any(word.endswith(x) for x in ('eer', 'ier', 'yer', 'ger', 'ster'))):
            stem = word[:-2]
            return stem + 'e' if _count_syllables(stem) == 1 else stem
    
    if word.endswith('age') and len(word) > 4:
        stem = word[:-3]
        return stem + 'e' if _count_syllables(stem) == 1 else stem
    
    if word.endswith(('hood', 'ship', 'dom')):
        return word[:-4]
    
    if word.endswith('eth'):
        return word[:-3]
    
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