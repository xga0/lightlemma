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
- Flexible tokenization functionality
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
from lightlemma import lemmatize, stem, tokenize, Tokenizer
from lightlemma import text_to_lemmas, text_to_stems

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

# Using the tokenizer
text = "This is a simple example of tokenization!"
tokens = tokenize(text)
print(tokens)  # Output: ["this", "is", "a", "simple", "example", "of", "tokenization"]

# Advanced tokenization with custom options
tokenizer = Tokenizer(preserve_case=True, preserve_punctuation=True)
custom_tokens = tokenizer.tokenize(text)
print(custom_tokens)  # Output: ["This", "is", "a", "simple", "example", "of", "tokenization", "!"]

# Complete text processing pipeline - manual approach
text = "The cats are running faster than dogs."
tokens = tokenize(text)
lemmas = [lemmatize(token) for token in tokens]
print(lemmas)  # Output: ["the", "cat", "be", "run", "fast", "than", "dog"]

# Using direct text-to-normalized-tokens functions
text = "The cats are running faster than dogs."
# Convert text directly to lemmatized tokens in one step
lemmatized_tokens = text_to_lemmas(text)
print(lemmatized_tokens)  # Output: ["the", "cat", "be", "run", "fast", "than", "dog"]

# Convert text directly to stemmed tokens in one step
stemmed_tokens = text_to_stems(text)
print(stemmed_tokens)  # Output: ["the", "cat", "are", "run", "faster", "than", "dog"]

# Direct conversion with case preservation after lemmatization
lemmatized_tokens = text_to_lemmas(text, preserve_original_case=True)
print(lemmatized_tokens)  # Output: ["The", "cat", "be", "run", "fast", "than", "dog"]

# Direct conversion with case preservation after stemming
stemmed_tokens = text_to_stems("The RUNNING cats", preserve_original_case=True)
print(stemmed_tokens)  # Output: ["The", "RUN", "cat"]
```

## Tokenization Options

The tokenizer provides several options for customizing the tokenization process:

- **pattern**: Custom regex pattern for tokenization
- **preserve_case**: Whether to preserve case of tokens
- **preserve_urls**: Whether to keep URLs as single tokens
- **preserve_emails**: Whether to keep email addresses as single tokens 
- **preserve_numbers**: Whether to keep numbers as tokens
- **preserve_punctuation**: Whether to include punctuation as separate tokens

## Text Processing Pipeline Functions

LightLemma provides convenient functions that process text directly to normalized tokens in a single step:

- **text_to_lemmas(text, tokenizer_options=None, preserve_original_case=False)**: Converts raw text directly to lemmatized tokens
- **text_to_stems(text, tokenizer_options=None, preserve_original_case=False)**: Converts raw text directly to stemmed tokens

These functions accept the following parameters:
- **text**: The input text to process
- **tokenizer_options**: Optional dictionary of tokenizer settings for customizing tokenization
- **preserve_original_case**: If True, maintains the original case pattern of tokens after lemmatization/stemming

The case preservation feature allows you to maintain the original capitalization of words even after they've been lemmatized or stemmed. This is particularly useful for proper nouns, title case text, or when you need to preserve the original formatting of the text.

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