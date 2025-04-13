"""
Core lemmatizer implementation.
"""
import json
import os
import re
import logging
from typing import Dict, Optional, Pattern, Tuple, Set

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Vowels for checking syllables
VOWELS = set('aeiou')

# Compile patterns once for better performance
PATTERNS = {
    # Noun patterns
    'plural': re.compile(r'(?:s|es|ies)$'),
    'latin_plural': re.compile(r'(?:a|i|ae|uses|ices|ices|ides|odes|ata)$'),
    'ves_plural': re.compile(r'ves$'),
    
    # Verb patterns
    'past': re.compile(r'(?:ed|d)$'),
    'ing': re.compile(r'ing$'),
    'ize': re.compile(r'ize$'),
    'ise': re.compile(r'ise$'),  # British spelling
    'ate': re.compile(r'ate$'),
    'en': re.compile(r'en$'),
    'ify': re.compile(r'ify$'),
    'fy': re.compile(r'fy$'),
    'eth': re.compile(r'eth$'),  # Archaic forms (e.g., sayeth)
    
    # Adjective patterns
    'ly': re.compile(r'ly$'),
    'ful': re.compile(r'ful$'),
    'able': re.compile(r'able$'),
    'ible': re.compile(r'ible$'),
    'al': re.compile(r'al$'),
    'ial': re.compile(r'ial$'),
    'ic': re.compile(r'ic$'),
    'ical': re.compile(r'ical$'),
    'ive': re.compile(r'ive$'),
    'ative': re.compile(r'ative$'),
    'ous': re.compile(r'ous$'),
    'ious': re.compile(r'ious$'),
    'ant': re.compile(r'ant$'),
    'ent': re.compile(r'ent$'),
    'most': re.compile(r'most$'),
    'ward': re.compile(r'ward$'),
    'wards': re.compile(r'wards$'),
    'wise': re.compile(r'wise$'),
    
    # Noun patterns
    'ment': re.compile(r'ment$'),
    'ness': re.compile(r'ness$'),
    'tion': re.compile(r'tion$'),
    'sion': re.compile(r'sion$'),
    'ation': re.compile(r'ation$'),
    'ition': re.compile(r'ition$'),
    'ance': re.compile(r'ance$'),
    'ence': re.compile(r'ence$'),
    'ity': re.compile(r'ity$'),
    'ety': re.compile(r'ety$'),
    'hood': re.compile(r'hood$'),
    'ship': re.compile(r'ship$'),
    'ian': re.compile(r'ian$'),
    'ist': re.compile(r'ist$'),
    'ism': re.compile(r'ism$'),
    'dom': re.compile(r'dom$'),
    'er': re.compile(r'er$'),
    'or': re.compile(r'or$'),
    'cy': re.compile(r'cy$'),
    'ry': re.compile(r'ry$'),
    'age': re.compile(r'age$')
}

# Double consonant endings that should be simplified
DOUBLE_CONSONANT_ENDINGS = {'bb', 'dd', 'ff', 'gg', 'mm', 'nn', 'pp', 'rr', 'tt', 'll'}

# Words that should keep their double consonants
KEEP_DOUBLE = {
    'fall', 'tell', 'roll', 'sell', 'small', 'spell', 'still', 'stall', 'skill',
    'chill', 'will', 'fill', 'full', 'doll', 'poll', 'tall', 'well'
}

# Common -ves plurals and their singular forms
VES_MAPPING = {
    'leaves': 'leaf',
    'lives': 'life',
    'selves': 'self',
    'wolves': 'wolf',
    'shelves': 'shelf',
    'calves': 'calf',
    'halves': 'half',
    'knives': 'knife',
    'wives': 'wife',
    'thieves': 'thief',
    'loaves': 'loaf',
    'hooves': 'hoof',
    'scarves': 'scarf',
    'wharves': 'wharf',
    'elves': 'elf'
}

def _count_syllables(word: str) -> int:
    """Count the number of syllables in a word."""
    word = word.lower()
    count = 0
    prev_is_vowel = False
    
    for char in word:
        is_vowel = char in VOWELS
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    
    # Handle silent e
    if word.endswith('e'):
        if not word.endswith(('le', 'ie', 'ee', 'ye')):
            count -= 1
    
    return max(1, count)  # Every word has at least one syllable

def _load_irregular_forms() -> Dict[str, str]:
    """Load irregular forms from the JSON data file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, 'data', 'irregular_forms.json')
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Flatten the dictionary and check for duplicates
            irregular_forms = {}
            seen_forms = set()
            for category, forms in data.items():
                for form, lemma in forms.items():
                    if form in seen_forms:
                        logger.warning(f"Duplicate irregular form found: {form}")
                    seen_forms.add(form)
                    irregular_forms[form] = lemma
            return irregular_forms
    except FileNotFoundError:
        logger.error(f"Irregular forms data file not found: {data_file}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in irregular forms data: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading irregular forms: {e}")
        return {}

# Load irregular forms at module import time
IRREGULAR_FORMS = _load_irregular_forms()

def _strip_double_consonants(word: str) -> str:
    """Strip double consonants at the end of the word if appropriate."""
    if len(word) > 2:
        if word[-2:] in DOUBLE_CONSONANT_ENDINGS and word not in KEEP_DOUBLE:
            return word[:-1]
    return word

def _handle_latin_plurals(word: str) -> Tuple[str, bool]:
    """Handle Latin and Greek origin plural forms."""
    if word.endswith('a'):
        if word.endswith('mena'):
            return word[:-4] + 'enon', True
        if word.endswith('mata'):
            return word[:-4] + 'ma', True
    elif word.endswith('i'):
        if word.endswith('alumni'):
            return word[:-1] + 'us', True
        if word.endswith('fungi'):
            return word[:-1] + 'us', True
        if word.endswith('cacti'):
            return word[:-1] + 'us', True
        if word.endswith('stimuli'):
            return word[:-1] + 'us', True
        if word.endswith('nuclei'):
            return word[:-1] + 'us', True
        if word.endswith('radii'):
            return word[:-1] + 'us', True
    elif word.endswith('ae'):
        if word.endswith('algae'):
            return word[:-2] + 'a', True
        if word.endswith('larvae'):
            return word[:-2] + 'a', True
        if word.endswith('nebulae'):
            return word[:-2] + 'a', True
    elif word.endswith('ices'):
        if len(word) > 5:  # Avoid changing words like 'spices'
            return word[:-4] + 'ex', True
    elif word.endswith('ides'):
        return word[:-4] + 'is', True  # chrysalides -> chrysalis
    elif word.endswith('odes'):
        return word[:-4] + 'is', True  # octopodes -> octopis
    elif word.endswith('ata'):
        return word[:-3] + 'a', True   # stigmata -> stigma
    elif word.endswith('uses'):
        if word.endswith('statuses'):
            return word[:-2], True
        if word.endswith('viruses'):
            return word[:-2], True
        if word.endswith('apparatuses'):
            return word[:-2], True
    return word, False

def _handle_ves_plurals(word: str) -> Tuple[str, bool]:
    """Handle words ending in -ves."""
    if word in VES_MAPPING:
        return VES_MAPPING[word], True
    if word.endswith('ves'):
        # Generic rule for -ves -> -f
        return word[:-3] + 'f', True
    return word, False

def _apply_rules(word: str) -> str:
    """Apply lemmatization rules to a word."""
    if word in IRREGULAR_FORMS:
        return IRREGULAR_FORMS[word]
    
    original = word
    
    # Try special plural forms first
    word, changed = _handle_latin_plurals(word)
    if changed:
        return word
    
    word, changed = _handle_ves_plurals(word)
    if changed:
        return word
    
    # Handle regular plurals
    if PATTERNS['plural'].search(word):
        if word.endswith('ies'):
            if len(word) > 4:  # Avoid changing words like "series"
                word = word[:-3] + 'y'
        elif word.endswith('es'):
            if word.endswith('sses'):
                word = word[:-2]  # addresses -> address
            elif word.endswith('xes'):
                word = word[:-2]  # boxes -> box
            elif word.endswith('ches'):
                word = word[:-2]  # watches -> watch
            elif word.endswith('shes'):
                word = word[:-2]  # wishes -> wish
            elif word.endswith('oes'):
                if len(word) > 4:  # Avoid changing "goes"
                    word = word[:-2]  # heroes -> hero
            else:
                word = word[:-1] if word.endswith('s') else word[:-2]
        elif word.endswith('s'):
            if not word.endswith(('ss', 'us', 'is')):  # Avoid changing words like "boss", "status", "basis"
                word = word[:-1]
    
    # Handle verb forms
    elif PATTERNS['past'].search(word):
        if word.endswith('ied'):
            if len(word) > 4:
                word = word[:-3] + 'y'  # studied -> study
            else:
                word = word[:-1]  # died -> die
        elif word.endswith('ed'):
            if len(word) > 4:
                if word.endswith('eed'):
                    if len(word) > 5:  # Avoid changing "feed" -> "fe"
                        word = word[:-1]  # agreed -> agree
                elif word.endswith('ied'):
                    word = word[:-3] + 'y'  # tried -> try
                else:
                    word = word[:-2]
                    word = _strip_double_consonants(word)
                    if _count_syllables(word) == 1:
                        word = word + 'e'  # saved -> save
    
    # Handle gerund forms
    elif PATTERNS['ing'].search(word):
        if len(word) > 4:
            base = word[:-3]
            if base[-1] == base[-2] and base[-1] in 'bdfglmnprst':  # doubled consonant
                if base[:-1] not in KEEP_DOUBLE:
                    word = base[:-1]
            else:
                word = base
                if word.endswith('at'):  # creating -> create
                    word = word + 'e'
                elif word.endswith('y'):  # studying -> study
                    pass
                elif len(word) > 3:
                    if _count_syllables(word) == 1:
                        word = word + 'e'  # riding -> ride
    
    # Handle other verb forms
    elif PATTERNS['ize'].search(word) or PATTERNS['ise'].search(word):
        return word  # These are usually base forms
    elif PATTERNS['ate'].search(word):
        return word  # These are usually base forms
    elif PATTERNS['ify'].search(word) or PATTERNS['fy'].search(word):
        return word  # These are usually base forms
    elif PATTERNS['eth'].search(word):
        word = word[:-3]  # sayeth -> say
    
    # Handle adjective forms
    elif PATTERNS['ly'].search(word):
        if word.endswith('ily'):
            word = word[:-3] + 'y'  # happily -> happy
        elif word.endswith('ly'):
            word = word[:-2]  # quickly -> quick
    elif PATTERNS['ful'].search(word):
        word = word[:-3]
    elif PATTERNS['able'].search(word) or PATTERNS['ible'].search(word):
        if word.endswith('able'):
            word = word[:-4]
        else:
            word = word[:-4]
        if word.endswith('at'):  # debatable -> debate
            word = word + 'e'
        elif _count_syllables(word) == 1:
            word = word + 'e'  # likable -> like
    elif PATTERNS['ous'].search(word) or PATTERNS['ious'].search(word):
        return word  # These are usually base forms
    elif PATTERNS['ant'].search(word) or PATTERNS['ent'].search(word):
        if len(word) > 5:  # Avoid changing short words
            word = word[:-3] + 'e'  # dependent -> depend
    elif PATTERNS['al'].search(word):
        if PATTERNS['ical'].search(word):
            word = word[:-4]
        else:
            word = word[:-2]
    elif any(PATTERNS[p].search(word) for p in ['most', 'ward', 'wards', 'wise']):
        return word  # These are usually complete words
    
    # Handle noun forms
    elif PATTERNS['ment'].search(word):
        word = word[:-4]
        if _count_syllables(word) == 1:
            word = word + 'e'  # statement -> state
    elif PATTERNS['ness'].search(word):
        word = word[:-4]
        if word.endswith('i'):
            word = word[:-1] + 'y'  # happiness -> happy
    elif PATTERNS['ation'].search(word) or PATTERNS['ition'].search(word):
        word = word[:-5] + 'e'
    elif PATTERNS['tion'].search(word) or PATTERNS['sion'].search(word):
        if len(word) > 5:  # Avoid changing short words
            word = word[:-3] + 'e'
    elif PATTERNS['ance'].search(word) or PATTERNS['ence'].search(word):
        word = word[:-4] + 'e'
    elif PATTERNS['ity'].search(word) or PATTERNS['ety'].search(word):
        word = word[:-3]
        if word.endswith('al'):
            word = word[:-2]
        if word.endswith('bil'):
            word = word[:-2] + 'le'
        elif word.endswith('iv'):
            word = word + 'e'
    elif PATTERNS['hood'].search(word) or PATTERNS['ship'].search(word) or PATTERNS['dom'].search(word):
        word = word[:-4]
    elif PATTERNS['er'].search(word) or PATTERNS['or'].search(word):
        if len(word) > 4:  # Avoid changing short words like "her"
            if not any(word.endswith(x) for x in ['eer', 'ier', 'yer', 'ger', 'ster']):
                word = word[:-2]
                if _count_syllables(word) == 1:
                    word = word + 'e'  # writer -> write
    elif PATTERNS['ism'].search(word) or PATTERNS['ist'].search(word):
        return word  # These are usually base forms
    elif PATTERNS['age'].search(word):
        if len(word) > 4:  # Avoid changing words like "age"
            word = word[:-3]
            if _count_syllables(word) == 1:
                word = word + 'e'  # usage -> use
    
    return word if word != original else original

def lemmatize(word: str) -> str:
    """
    Lemmatize an English word to its base form.
    
    Args:
        word: The word to lemmatize.
        
    Returns:
        The lemmatized form of the word.
    """
    if not word:
        return word
    
    # Convert to lowercase for processing
    word = word.lower()
    
    # Apply rules
    return _apply_rules(word) 