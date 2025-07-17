"""
LightLemma: A lightweight, fast English lemmatizer and stemmer.
"""

from .lemmatizer import lemmatize, lemmatize_batch
from .stemmer import stem, stem_batch
from .tokenizer import (
    tokenize, tokenize_cached, tokenize_batch, Tokenizer, 
    text_to_lemmas, text_to_stems, text_to_lemmas_batch, text_to_stems_batch
)

__version__ = "0.1.4"
__all__ = [
    "lemmatize", "lemmatize_batch", "stem", "stem_batch", 
    "tokenize", "tokenize_cached", "tokenize_batch", "Tokenizer", 
    "text_to_lemmas", "text_to_stems", "text_to_lemmas_batch", "text_to_stems_batch"
] 