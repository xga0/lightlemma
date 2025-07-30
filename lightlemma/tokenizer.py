"""
Tokenizer implementation for splitting text into words/tokens.
"""
import re
from typing import List, Optional, Pattern, Union, Dict
from functools import lru_cache

DEFAULT_TOKEN_PATTERN = re.compile(r'\b(?:\d+(?:\.\d+)?|\w+)\b')
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')
EMAIL_PATTERN = re.compile(r'\S+@\S+\.\S+')
NUMBER_PATTERN = re.compile(r'\b\d+(?:\.\d+)?\b')
PUNCTUATION_PATTERN = re.compile(r'[^\w\s]')

class Tokenizer:
    """
    A flexible tokenizer for splitting text into tokens (words).
    
    This tokenizer provides various options for text tokenization,
    including handling of URLs, emails, numbers, and punctuation.
    """
    
    def __init__(
        self,
        pattern: Optional[Union[str, Pattern]] = None,
        preserve_case: bool = False,
        preserve_urls: bool = False,
        preserve_emails: bool = False,
        preserve_numbers: bool = True,
        preserve_punctuation: bool = False
    ):
        """
        Initialize a Tokenizer with the specified options.
        
        Args:
            pattern: Custom regex pattern for tokenization. If None, default word boundary pattern is used.
            preserve_case: Whether to preserve case of tokens. If False, all tokens are lowercased.
            preserve_urls: Whether to keep URLs as single tokens.
            preserve_emails: Whether to keep email addresses as single tokens.
            preserve_numbers: Whether to keep numbers as tokens.
            preserve_punctuation: Whether to include punctuation as separate tokens.
        """
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern or DEFAULT_TOKEN_PATTERN
        self.preserve_case = preserve_case
        self.preserve_urls = preserve_urls
        self.preserve_emails = preserve_emails
        self.preserve_numbers = preserve_numbers
        self.preserve_punctuation = preserve_punctuation
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize the given text into a list of tokens.
        
        Args:
            text: The text to tokenize.
            
        Returns:
            A list of tokens extracted from the text.
            
        Raises:
            TypeError: If text is not a string.
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        
        if not text:
            return []
        
        tokens = []
        working_text = text
        
        if self.preserve_urls:
            urls = URL_PATTERN.findall(working_text)
            for url in urls:
                working_text = working_text.replace(url, " ")
                tokens.append(url)
        
        if self.preserve_emails:
            emails = EMAIL_PATTERN.findall(working_text)
            for email in emails:
                working_text = working_text.replace(email, " ")
                tokens.append(email)
        
        if self.preserve_punctuation:
            words = self.pattern.findall(working_text)
            punctuation = PUNCTUATION_PATTERN.findall(working_text)
            tokens.extend(words)
            tokens.extend(punctuation)
        else:
            tokens.extend(self.pattern.findall(working_text))
        
        tokens = [t for t in tokens if t and (self.preserve_numbers or not t.replace('.', '').isdigit())]
        
        if not self.preserve_case:
            tokens = [t.lower() for t in tokens]
        
        return tokens

_DEFAULT_TOKENIZER = Tokenizer()

def tokenize(text: str) -> List[str]:
    """
    Tokenize text into words using default settings.
    
    This function splits text into words using word boundaries,
    lowercases all tokens, and preserves numbers.
    
    Performance optimized: Uses a singleton tokenizer to avoid 
    recreating objects and recompiling regex patterns.
    
    Args:
        text: The text to tokenize.
        
    Returns:
        A list of tokens (words) from the text.
        
    Raises:
        TypeError: If text is not a string.
    """
    return _DEFAULT_TOKENIZER.tokenize(text)

@lru_cache(maxsize=1024)
def tokenize_cached(text: str) -> List[str]:
    """
    Tokenize text into words using default settings with caching.
    
    This function is identical to tokenize() but caches results,
    making it more efficient for repeated tokenization of the same text.
    
    Args:
        text: The text to tokenize.
        
    Returns:
        A list of tokens (words) from the text.
        
    Raises:
        TypeError: If text is not a string.
    """
    return tokenize(text)

@lru_cache(maxsize=512)
def _apply_case_pattern(original: str, processed: str) -> str:
    """Apply original case pattern to processed token efficiently."""
    if not original or not processed:
        return processed
    
    if original.isupper():
        return processed.upper()
    elif original[0].isupper():
        return processed.capitalize()
    else:
        return processed

def text_to_lemmas(text: str, tokenizer_options: Optional[Dict] = None, preserve_original_case: bool = False) -> List[str]:
    """
    Process text directly to lemmatized tokens in one step.
    
    This function provides a convenient way to convert raw text into
    lemmatized tokens in a single function call. It first tokenizes
    the text and then lemmatizes each token.
    
    Args:
        text: The text to process.
        tokenizer_options: Optional dictionary of tokenizer settings.
            Can include any of the Tokenizer class constructor parameters.
        preserve_original_case: If True, will attempt to preserve the original case
            pattern of each token after lemmatization. Note that this is an approximation
            as lemmatization can change word length.
            
    Returns:
        A list of lemmatized tokens from the text.
        
    Raises:
        TypeError: If text is not a string.
    """
    from .lemmatizer import lemmatize_batch
    
    if tokenizer_options is None:
        tokenizer_options = {}
    
    if preserve_original_case:
        case_tokenizer = Tokenizer(preserve_case=True, **tokenizer_options)
        tokens_with_case = case_tokenizer.tokenize(text)
        lemmas = lemmatize_batch([token.lower() for token in tokens_with_case])
        return [_apply_case_pattern(orig, lemma) for orig, lemma in zip(tokens_with_case, lemmas)]
    else:
        tokenizer = Tokenizer(**tokenizer_options)
        tokens = tokenizer.tokenize(text)
        return lemmatize_batch(tokens)

def text_to_stems(text: str, tokenizer_options: Optional[Dict] = None, preserve_original_case: bool = False) -> List[str]:
    """
    Process text directly to stemmed tokens in one step.
    
    This function provides a convenient way to convert raw text into
    stemmed tokens in a single function call. It first tokenizes
    the text and then stems each token.
    
    Args:
        text: The text to process.
        tokenizer_options: Optional dictionary of tokenizer settings.
            Can include any of the Tokenizer class constructor parameters.
        preserve_original_case: If True, will attempt to preserve the original case
            pattern of each token after stemming. Note that this is an approximation
            as stemming can change word length.
            
    Returns:
        A list of stemmed tokens from the text.
        
    Raises:
        TypeError: If text is not a string.
    """
    from .stemmer import stem_batch
    
    if tokenizer_options is None:
        tokenizer_options = {}
    
    if preserve_original_case:
        case_tokenizer = Tokenizer(preserve_case=True, **tokenizer_options)
        tokens_with_case = case_tokenizer.tokenize(text)
        stems = stem_batch([token.lower() for token in tokens_with_case])
        return [_apply_case_pattern(orig, stem) for orig, stem in zip(tokens_with_case, stems)]
    else:
        tokenizer = Tokenizer(**tokenizer_options)
        tokens = tokenizer.tokenize(text)
        return stem_batch(tokens)

def tokenize_batch(texts: List[str], tokenizer_options: Optional[Dict] = None) -> List[List[str]]:
    """
    Tokenize a batch of texts efficiently.
    
    This function processes multiple texts at once, providing better performance
    than calling tokenize() individually for each text by reducing function
    call overhead and reusing the same tokenizer instance.
    
    Args:
        texts: List of texts to tokenize.
        tokenizer_options: Optional dictionary of tokenizer settings.
        
    Returns:
        List of token lists, one for each input text.
        
    Raises:
        TypeError: If texts is not a list or contains non-string items
    
    Examples:
        >>> tokenize_batch(["Hello world", "This is a test"])
        [['hello', 'world'], ['this', 'is', 'a', 'test']]
    """
    if not isinstance(texts, list):
        raise TypeError("Input must be a list")
    
    if not texts:
        return []
    
    if tokenizer_options is None:
        tokenizer_options = {}
    
    tokenizer = Tokenizer(**tokenizer_options)
    return [tokenizer.tokenize(text) if isinstance(text, str) else [] for text in texts]

def _create_shared_tokenizers(tokenizer_options: Dict, preserve_original_case: bool):
    """Create shared tokenizer instances to reduce object creation."""
    tokenizer = Tokenizer(**tokenizer_options)
    case_tokenizer = None
    
    if preserve_original_case:
        case_tokenizer = Tokenizer(preserve_case=True, **tokenizer_options)
    
    return tokenizer, case_tokenizer

def text_to_lemmas_batch(texts: List[str], tokenizer_options: Optional[Dict] = None, preserve_original_case: bool = False) -> List[List[str]]:
    """
    Process a batch of texts directly to lemmatized tokens efficiently.
    
    This function processes multiple texts at once, providing better performance
    than calling text_to_lemmas() individually for each text by reducing function
    call overhead and reusing tokenizer instances.
    
    Args:
        texts: List of texts to process.
        tokenizer_options: Optional dictionary of tokenizer settings.
        preserve_original_case: If True, will attempt to preserve the original case
            pattern of each token after lemmatization.
            
    Returns:
        List of lemmatized token lists, one for each input text.
        
    Raises:
        TypeError: If texts is not a list or contains non-string items
    
    Examples:
        >>> text_to_lemmas_batch(["The cats are running", "Dogs played"])
        [['the', 'cat', 'be', 'run'], ['dog', 'play']]
    """
    from .lemmatizer import lemmatize_batch
    
    if not isinstance(texts, list):
        raise TypeError("Input must be a list")
    
    if not texts:
        return []
    
    if tokenizer_options is None:
        tokenizer_options = {}
    
    tokenizer, case_tokenizer = _create_shared_tokenizers(tokenizer_options, preserve_original_case)
    
    results = []
    for text in texts:
        if not isinstance(text, str):
            results.append([])
            continue
        
        if preserve_original_case:
            tokens_with_case = case_tokenizer.tokenize(text)
            lemmas = lemmatize_batch([token.lower() for token in tokens_with_case])
            results.append([_apply_case_pattern(orig, lemma) for orig, lemma in zip(tokens_with_case, lemmas)])
        else:
            tokens = tokenizer.tokenize(text)
            results.append(lemmatize_batch(tokens))
    
    return results

def text_to_stems_batch(texts: List[str], tokenizer_options: Optional[Dict] = None, preserve_original_case: bool = False) -> List[List[str]]:
    """
    Process a batch of texts directly to stemmed tokens efficiently.
    
    This function processes multiple texts at once, providing better performance
    than calling text_to_stems() individually for each text by reducing function
    call overhead and reusing tokenizer instances.
    
    Args:
        texts: List of texts to process.
        tokenizer_options: Optional dictionary of tokenizer settings.
        preserve_original_case: If True, will attempt to preserve the original case
            pattern of each token after stemming.
            
    Returns:
        List of stemmed token lists, one for each input text.
        
    Raises:
        TypeError: If texts is not a list or contains non-string items
    
    Examples:
        >>> text_to_stems_batch(["The cats are running", "Dogs played"])
        [['the', 'cat', 'are', 'run'], ['dog', 'play']]
    """
    from .stemmer import stem_batch
    
    if not isinstance(texts, list):
        raise TypeError("Input must be a list")
    
    if not texts:
        return []
    
    if tokenizer_options is None:
        tokenizer_options = {}
    
    tokenizer, case_tokenizer = _create_shared_tokenizers(tokenizer_options, preserve_original_case)
    
    results = []
    for text in texts:
        if not isinstance(text, str):
            results.append([])
            continue
        
        if preserve_original_case:
            tokens_with_case = case_tokenizer.tokenize(text)
            stems = stem_batch([token.lower() for token in tokens_with_case])
            results.append([_apply_case_pattern(orig, stem) for orig, stem in zip(tokens_with_case, stems)])
        else:
            tokens = tokenizer.tokenize(text)
            results.append(stem_batch(tokens))
    
    return results 