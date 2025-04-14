"""
LightLemma: A lightweight, fast English lemmatizer and stemmer.
"""

from .lemmatizer import lemmatize
from .stemmer import stem

__version__ = "0.1.2"
__all__ = ["lemmatize", "stem"] 