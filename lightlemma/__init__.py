"""
LightLemma: A lightweight, fast English lemmatizer and stemmer.
"""

from .lemmatizer import lemmatize
from .stemmer import stem
from .tokenizer import tokenize, tokenize_cached, Tokenizer, text_to_lemmas, text_to_stems

__version__ = "0.1.2"
__all__ = ["lemmatize", "stem", "tokenize", "tokenize_cached", "Tokenizer", "text_to_lemmas", "text_to_stems"] 