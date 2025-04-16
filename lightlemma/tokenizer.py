"""
Tokenizer implementation for splitting text into words/tokens.
"""
import re
from typing import List, Optional, Pattern, Union
from functools import lru_cache

# Compile patterns once for better performance
DEFAULT_TOKEN_PATTERN = re.compile(r'\b\w+\b')
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
        
        # Handle special cases first (URLs, emails)
        tokens = []
        working_text = text
        
        # Extract and preserve URLs if requested
        if self.preserve_urls:
            urls = URL_PATTERN.findall(working_text)
            for url in urls:
                working_text = working_text.replace(url, " <URL> ")
                tokens.append(url)
        
        # Extract and preserve emails if requested
        if self.preserve_emails:
            emails = EMAIL_PATTERN.findall(working_text)
            for email in emails:
                working_text = working_text.replace(email, " <EMAIL> ")
                tokens.append(email)
        
        # Handle the main tokenization
        if self.preserve_punctuation:
            # Extract words first
            words = self.pattern.findall(working_text)
            
            # Then extract punctuation as separate tokens
            punctuation = PUNCTUATION_PATTERN.findall(working_text)
            
            # Combine both sets of tokens
            tokens.extend(words)
            tokens.extend(punctuation)
        else:
            # Just extract words based on the pattern
            tokens.extend(self.pattern.findall(working_text))
        
        # Filter out empty tokens and handle case
        tokens = [t for t in tokens if t and (self.preserve_numbers or not t.isdigit())]
        
        if not self.preserve_case:
            tokens = [t.lower() for t in tokens]
        
        return tokens

# Provide simple functions for common use cases
def tokenize(text: str) -> List[str]:
    """
    Tokenize text into words using default settings.
    
    This function splits text into words using word boundaries,
    lowercases all tokens, and preserves numbers.
    
    Args:
        text: The text to tokenize.
        
    Returns:
        A list of tokens (words) from the text.
        
    Raises:
        TypeError: If text is not a string.
    """
    tokenizer = Tokenizer()
    return tokenizer.tokenize(text)


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


# Chain functions for combined tokenization and normalization
def text_to_lemmas(text: str, tokenizer_options: Optional[dict] = None, preserve_original_case: bool = False) -> List[str]:
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
    from .lemmatizer import lemmatize
    
    if tokenizer_options is None:
        tokenizer_options = {}
    
    # Make a copy to avoid modifying the original
    options = dict(tokenizer_options)
    
    # Always preserve case during tokenization if we want to preserve it after lemmatization
    if preserve_original_case and 'preserve_case' not in options:
        options['preserve_case'] = True
    
    tokenizer = Tokenizer(**options)
    tokens = tokenizer.tokenize(text)
    
    # Store original case pattern if needed
    if preserve_original_case:
        result = []
        for token in tokens:
            lemma = lemmatize(token.lower())
            # Try to apply original capitalization pattern
            if token.isupper():
                # All uppercase
                result.append(lemma.upper())
            elif token[0].isupper() and token[1:].islower():
                # Capitalized
                result.append(lemma.capitalize())
            elif token[0].isupper():
                # First letter uppercase, but not all lowercase after
                # (e.g. "CamelCase") - just capitalize in this case
                result.append(lemma.capitalize())
            else:
                # Keep lowercase
                result.append(lemma)
        return result
    else:
        # Standard processing - lemmatize all tokens
        return [lemmatize(token) for token in tokens]


def text_to_stems(text: str, tokenizer_options: Optional[dict] = None, preserve_original_case: bool = False) -> List[str]:
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
    from .stemmer import stem
    
    if tokenizer_options is None:
        tokenizer_options = {}
    
    # Make a copy to avoid modifying the original
    options = dict(tokenizer_options)
    
    # Always preserve case during tokenization if we want to preserve it after stemming
    if preserve_original_case and 'preserve_case' not in options:
        options['preserve_case'] = True
    
    tokenizer = Tokenizer(**options)
    tokens = tokenizer.tokenize(text)
    
    # Store original case pattern if needed
    if preserve_original_case:
        result = []
        for token in tokens:
            stemmed = stem(token.lower())
            # Try to apply original capitalization pattern
            if token.isupper():
                # All uppercase
                result.append(stemmed.upper())
            elif token[0].isupper() and token[1:].islower():
                # Capitalized
                result.append(stemmed.capitalize())
            elif token[0].isupper():
                # First letter uppercase, but not all lowercase after
                # (e.g. "CamelCase") - just capitalize in this case
                result.append(stemmed.capitalize())
            else:
                # Keep lowercase
                result.append(stemmed)
        return result
    else:
        # Standard processing - stem all tokens
        return [stem(token) for token in tokens] 