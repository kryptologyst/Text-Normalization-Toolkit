#!/usr/bin/env python3
"""
Simple demo script for Text Normalization Toolkit
This script demonstrates the basic functionality without requiring all dependencies.
"""

import re
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class NormalizationMethod(Enum):
    """Available normalization methods."""
    BASIC = "basic"
    ADVANCED = "advanced"
    CUSTOM = "custom"


@dataclass
class NormalizationConfig:
    """Configuration for text normalization."""
    lowercase: bool = True
    remove_punctuation: bool = True
    remove_numbers: bool = True
    remove_extra_whitespace: bool = True
    remove_stopwords: bool = True
    expand_contractions: bool = True
    remove_urls: bool = True
    remove_emails: bool = True
    min_word_length: int = 2
    max_word_length: int = 50
    language: str = "en"


class SimpleTextNormalizer:
    """Simple text normalizer for demonstration."""
    
    def __init__(self, config: Optional[NormalizationConfig] = None):
        """Initialize the normalizer with configuration."""
        self.config = config or NormalizationConfig()
        
        # Basic English stop words
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with'
        }
    
    def normalize(self, text: str, method: NormalizationMethod = NormalizationMethod.BASIC) -> Dict[str, Any]:
        """
        Normalize text using specified method.
        
        Args:
            text: Input text to normalize
            method: Normalization method to use
            
        Returns:
            Dictionary containing normalized text and metadata
        """
        if not text or not isinstance(text, str):
            return {"normalized_text": "", "metadata": {"error": "Invalid input text"}}
            
        original_text = text
        metadata = {
            "original_length": len(text),
            "method": method.value,
            "steps_applied": []
        }
        
        try:
            if method == NormalizationMethod.BASIC:
                normalized = self._basic_normalize(text)
            elif method == NormalizationMethod.ADVANCED:
                normalized = self._advanced_normalize(text)
            else:
                normalized = self._custom_normalize(text)
                
            metadata["final_length"] = len(normalized)
            metadata["compression_ratio"] = metadata["final_length"] / metadata["original_length"] if metadata["original_length"] > 0 else 0
            
            return {
                "normalized_text": normalized,
                "metadata": metadata
            }
            
        except Exception as e:
            return {
                "normalized_text": "",
                "metadata": {"error": str(e)}
            }
    
    def _basic_normalize(self, text: str) -> str:
        """Basic normalization using traditional methods."""
        # Lowercase
        if self.config.lowercase:
            text = text.lower()
            
        # Remove URLs
        if self.config.remove_urls:
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            
        # Remove emails
        if self.config.remove_emails:
            text = re.sub(r'\S+@\S+', '', text)
            
        # Expand contractions
        if self.config.expand_contractions:
            contractions = {
                "can't": "cannot",
                "won't": "will not",
                "n't": " not",
                "'re": " are",
                "'s": " is",
                "'d": " would",
                "'ll": " will",
                "'ve": " have",
                "'m": " am"
            }
            for contraction, expansion in contractions.items():
                text = text.replace(contraction, expansion)
            
        # Remove punctuation and numbers
        if self.config.remove_punctuation:
            text = re.sub(r'[^a-zA-Z\s]', '', text)
            
        # Remove extra whitespace
        if self.config.remove_extra_whitespace:
            text = re.sub(r'\s+', ' ', text).strip()
            
        # Tokenize and process
        tokens = text.split()
        
        # Remove stopwords
        if self.config.remove_stopwords:
            tokens = [token for token in tokens if token not in self.stop_words]
            
        # Filter by length
        tokens = [token for token in tokens 
                 if self.config.min_word_length <= len(token) <= self.config.max_word_length]
        
        return " ".join(tokens)
    
    def _advanced_normalize(self, text: str) -> str:
        """Advanced normalization (simplified version)."""
        # Apply basic normalization first
        normalized = self._basic_normalize(text)
        
        # Additional processing could go here
        # For now, just return the basic normalized text
        return normalized
    
    def _custom_normalize(self, text: str) -> str:
        """Custom normalization based on configuration."""
        # Apply basic normalization
        return self._basic_normalize(text)
    
    def get_text_quality_metrics(self, text: str) -> Dict[str, Any]:
        """Calculate text quality metrics."""
        if not text:
            return {}
            
        metrics = {
            "length": len(text),
            "word_count": len(text.split()),
            "avg_word_length": sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0,
            "punctuation_ratio": len(re.findall(r'[^\w\s]', text)) / len(text) if text else 0,
            "uppercase_ratio": len(re.findall(r'[A-Z]', text)) / len(text) if text else 0,
            "digit_ratio": len(re.findall(r'\d', text)) / len(text) if text else 0,
            "whitespace_ratio": len(re.findall(r'\s', text)) / len(text) if text else 0,
        }
        
        return metrics


def main():
    """Demo the simple text normalizer."""
    print("🧠 Text Normalization Toolkit - Simple Demo")
    print("=" * 60)
    
    # Sample texts for testing
    sample_texts = [
        "Running, jumping, and swimming are fun activities! But are they productive?",
        "I can't believe it's already 2024! Check out https://example.com for more info.",
        "The quick brown fox jumps over the lazy dog. It's amazing!",
        "Email me at john.doe@example.com or call (555) 123-4567.",
        "This is a test with special characters and extra    spaces."
    ]
    
    # Initialize normalizer
    config = NormalizationConfig(
        remove_urls=True,
        remove_emails=True,
        expand_contractions=True
    )
    normalizer = SimpleTextNormalizer(config)
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\n📝 Sample {i}:")
        print(f"Original: {text}")
        
        # Test different methods
        for method in NormalizationMethod:
            result = normalizer.normalize(text, method)
            print(f"{method.value.title()}: {result['normalized_text']}")
            
        # Get quality metrics
        metrics = normalizer.get_text_quality_metrics(text)
        print(f"Quality metrics: Length={metrics['length']}, Words={metrics['word_count']}, Avg word length={metrics['avg_word_length']:.1f}")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"\n📋 Next steps:")
    print(f"1. Install dependencies: pip install -r requirements.txt")
    print(f"2. Run full demo: python core_normalizer.py")
    print(f"3. Start API: python api.py")
    print(f"4. Start UI: streamlit run ui.py")


if __name__ == "__main__":
    main()
