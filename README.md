# LightLemma

[![PyPI version](https://img.shields.io/pypi/v/lightlemma.svg)](https://pypi.org/project/lightlemma/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lightlemma.svg)](https://pypi.org/project/lightlemma/)

A lightweight, fast English lemmatizer and stemmer. LightLemma focuses on providing high-performance text normalization for English text while maintaining a minimal footprint.

## Introduction to Lemmatization

Lemmatization is the process of reducing words to their base or dictionary form (lemma). This process uses morphological analysis and dictionary lookups to transform words into their canonical forms. For example:
- "running" → "run"
- "better" → "good"
- "studies" → "study"
- "am", "are", "is" → "be"

Unlike stemming, lemmatization considers the context and part of speech of words to produce linguistically valid results. It uses a dictionary-based approach to ensure the output is always a real word.

## The Difference Between Lemmatization and Stemming

While both lemmatization and stemming aim to reduce words to their base form, they work differently:

**Lemmatization:**
- Produces linguistically valid words
- Uses dictionary lookup and morphological analysis
- Considers word context and part of speech
- More accurate but typically slower
- Example: "studies" → "study"

**Stemming:**
- Uses rule-based algorithms to strip affixes
- Faster but can produce non-words
- Doesn't consider word context
- More aggressive reduction
- Example: "studies" → "studi"

Choose lemmatization when you need linguistically accurate results, and stemming when you need fast, approximate word normalization.

## Features

- Fast and lightweight English lemmatization
- Porter Stemmer implementation
- Simple, easy-to-use API
- No external dependencies
- Optimized for performance
- Future integration with contraction_fix and emoticon_fix

## Installation

```bash
pip install lightlemma
```

## Usage

```python
from lightlemma import lemmatize, stem

# Simple word lemmatization
word = "running"
lemma = lemmatize(word)
print(lemma)  # Output: "run"

# Process multiple words with lemmatization
words = ["cats", "running", "better", "studies"]
lemmas = [lemmatize(word) for word in words]
print(lemmas)  # Output: ["cat", "run", "good", "study"]

# Using the Porter Stemmer
word = "running"
stemmed = stem(word)
print(stemmed)  # Output: "run"

# Compare lemmatization vs stemming
words = ["studies", "universal", "maximum"]
lemmas = [lemmatize(word) for word in words]
stems = [stem(word) for word in words]
print(lemmas)  # Output: ["study", "universal", "maximum"]
print(stems)   # Output: ["studi", "univers", "maxim"]
```

## Performance

LightLemma is designed to be faster and more memory-efficient than existing solutions while maintaining high accuracy for English text.

## Future Features

- Integration with contraction_fix for handling contractions
- Integration with emoticon_fix for emoticon normalization
- Support for additional text normalization features

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 