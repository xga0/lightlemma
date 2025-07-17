"""
Tests for the tokenizer module.
"""
import re
import unittest
from lightlemma.tokenizer import tokenize, tokenize_cached, Tokenizer, text_to_lemmas, text_to_stems

class TestTokenizer(unittest.TestCase):
    """Test cases for the tokenizer functionality."""
    
    def test_empty_string(self):
        """Test tokenization of an empty string."""
        self.assertEqual(tokenize(""), [])
    
    def test_basic_tokenization(self):
        """Test basic tokenization of a simple sentence."""
        text = "This is a simple test."
        expected = ["this", "is", "a", "simple", "test"]
        self.assertEqual(tokenize(text), expected)
    
    def test_punctuation(self):
        """Test tokenization with punctuation."""
        text = "Hello, world! How are you? I'm fine."
        expected = ["hello", "world", "how", "are", "you", "i", "m", "fine"]
        self.assertEqual(tokenize(text), expected)
    
    def test_numbers(self):
        """Test tokenization with numbers."""
        text = "I have 42 apples and 3.14 pies."
        expected = ["i", "have", "42", "apples", "and", "3.14", "pies"]
        self.assertEqual(tokenize(text), expected)
    
    def test_preserve_case(self):
        """Test tokenization with case preservation."""
        text = "Hello World"
        tokenizer = Tokenizer(preserve_case=True)
        self.assertEqual(tokenizer.tokenize(text), ["Hello", "World"])
    
    def test_urls(self):
        """Test tokenization with URLs."""
        text = "Visit https://example.com for more info."
        
        # Default tokenizer should split the URL
        default_tokens = tokenize(text)
        self.assertNotIn("https://example.com", default_tokens)
        
        # Tokenizer with URL preservation should keep the URL intact
        tokenizer = Tokenizer(preserve_urls=True)
        tokens = tokenizer.tokenize(text)
        self.assertIn("https://example.com", tokens)
    
    def test_emails(self):
        """Test tokenization with email addresses."""
        text = "Contact user@example.com for support."
        
        # Default tokenizer should split the email
        default_tokens = tokenize(text)
        self.assertNotIn("user@example.com", default_tokens)
        
        # Tokenizer with email preservation should keep the email intact
        tokenizer = Tokenizer(preserve_emails=True)
        tokens = tokenizer.tokenize(text)
        self.assertIn("user@example.com", tokens)
    
    def test_custom_pattern(self):
        """Test tokenization with a custom pattern."""
        # Pattern to match only capitalized words
        tokenizer = Tokenizer(pattern=r'\b[A-Z][a-z]*\b', preserve_case=True)
        text = "The Quick Brown Fox Jumps Over the Lazy Dog"
        expected = ["The", "Quick", "Brown", "Fox", "Jumps", "Over", "Lazy", "Dog"]
        self.assertEqual(tokenizer.tokenize(text), expected)
    
    def test_preserve_punctuation(self):
        """Test tokenization with punctuation preservation."""
        text = "Hello, world!"
        tokenizer = Tokenizer(preserve_punctuation=True)
        tokens = tokenizer.tokenize(text)
        self.assertTrue("," in tokens or "," in "".join(tokens))
        self.assertTrue("!" in tokens or "!" in "".join(tokens))
    
    def test_cached_tokenization(self):
        """Test cached tokenization for repeated text."""
        text = "This is a test of the cached tokenizer."
        result1 = tokenize_cached(text)
        result2 = tokenize_cached(text)
        # Should return the same object (from cache)
        self.assertIs(result1, result2)
    
    def test_error_handling(self):
        """Test error handling for invalid input."""
        with self.assertRaises(TypeError):
            tokenize(123)
        
        with self.assertRaises(TypeError):
            tokenizer = Tokenizer()
            tokenizer.tokenize(None)
    
    def test_text_to_lemmas(self):
        """Test direct text to lemmas conversion."""
        text = "The cats are running faster than dogs."
        result = text_to_lemmas(text)
        expected = ["the", "cat", "be", "run", "fast", "than", "dog"]
        self.assertEqual(result, expected)
        
        # Test with preserve_original_case
        result = text_to_lemmas(text, preserve_original_case=True)
        # First word should be capitalized (preserving original case)
        self.assertEqual(result[0], "The")
        # Others should maintain their original case
        self.assertEqual(result[1], "cat")  # "cats" -> "cat" (lowercase preserved)
        self.assertEqual(result[2], "be")   # "are" -> "be" (lowercase preserved)
    
    def test_text_to_stems(self):
        """Test direct text to stems conversion."""
        text = "The studies are showing interesting results."
        result = text_to_stems(text)
        # Expect stemmed tokens like "studi" instead of "study"
        self.assertIn("studi", result)
        self.assertIn("show", result)
        self.assertIn("interest", result)
        self.assertIn("result", result)
        
        # Test with preserve_original_case
        result = text_to_stems(text, preserve_original_case=True)
        # First word should be capitalized (preserving original case)
        self.assertEqual(result[0], "The")
        # Check that other words maintain their original case
        self.assertEqual(result[1], "studi")  # "studies" -> "studi" (lowercase preserved)
        
        # Test with mixed-case words
        text = "CamelCase UPPERCASE lowercase"
        result = text_to_stems(text, preserve_original_case=True)
        self.assertEqual(result[0], "Camelcas")  # "CamelCase" -> "Camelcas"
        self.assertEqual(result[1], "UPPERCAS") # "UPPERCASE" -> "UPPERCAS"
        self.assertEqual(result[2], "lowercas") # "lowercase" -> "lowercas"

if __name__ == "__main__":
    unittest.main() 