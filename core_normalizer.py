"""
Modern Text Normalization Toolkit

A comprehensive toolkit for text normalization using the latest NLP techniques
and libraries including spaCy, transformers, and advanced preprocessing methods.
"""

import re
import unicodedata
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import json

# Core NLP libraries
import spacy
import nltk
from transformers import AutoTokenizer, AutoModel
import torch

# Text processing utilities
import regex
import unidecode
import emoji
import contractions

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except Exception as e:
    logging.warning(f"NLTK download failed: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NormalizationMethod(Enum):
    """Available normalization methods."""
    BASIC = "basic"
    ADVANCED = "advanced"
    TRANSFORMER = "transformer"
    CUSTOM = "custom"


@dataclass
class NormalizationConfig:
    """Configuration for text normalization."""
    lowercase: bool = True
    remove_punctuation: bool = True
    remove_numbers: bool = True
    remove_extra_whitespace: bool = True
    remove_stopwords: bool = True
    lemmatize: bool = True
    stem: bool = False
    expand_contractions: bool = True
    normalize_unicode: bool = True
    remove_emojis: bool = False
    remove_urls: bool = True
    remove_emails: bool = True
    min_word_length: int = 2
    max_word_length: int = 50
    language: str = "en"
    custom_stopwords: Optional[List[str]] = None


class ModernTextNormalizer:
    """Modern text normalizer with advanced features."""
    
    def __init__(self, config: Optional[NormalizationConfig] = None):
        """Initialize the normalizer with configuration."""
        self.config = config or NormalizationConfig()
        self._load_models()
        
    def _load_models(self):
        """Load required NLP models."""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model successfully")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
            
        # Load NLTK components
        try:
            from nltk.corpus import stopwords
            from nltk.stem import PorterStemmer, WordNetLemmatizer
            
            self.stop_words = set(stopwords.words(self.config.language))
            if self.config.custom_stopwords:
                self.stop_words.update(self.config.custom_stopwords)
                
            self.stemmer = PorterStemmer()
            self.lemmatizer = WordNetLemmatizer()
            
        except Exception as e:
            logger.error(f"Failed to load NLTK components: {e}")
            self.stop_words = set()
            self.stemmer = None
            self.lemmatizer = None
    
    def normalize(self, text: str, method: NormalizationMethod = NormalizationMethod.ADVANCED) -> Dict[str, Any]:
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
            elif method == NormalizationMethod.TRANSFORMER:
                normalized = self._transformer_normalize(text)
            else:
                normalized = self._custom_normalize(text)
                
            metadata["final_length"] = len(normalized)
            metadata["compression_ratio"] = metadata["final_length"] / metadata["original_length"] if metadata["original_length"] > 0 else 0
            
            return {
                "normalized_text": normalized,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return {
                "normalized_text": "",
                "metadata": {"error": str(e)}
            }
    
    def _basic_normalize(self, text: str) -> str:
        """Basic normalization using traditional methods."""
        steps = []
        
        # Lowercase
        if self.config.lowercase:
            text = text.lower()
            steps.append("lowercase")
            
        # Remove URLs
        if self.config.remove_urls:
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            steps.append("remove_urls")
            
        # Remove emails
        if self.config.remove_emails:
            text = re.sub(r'\S+@\S+', '', text)
            steps.append("remove_emails")
            
        # Expand contractions
        if self.config.expand_contractions:
            text = contractions.fix(text)
            steps.append("expand_contractions")
            
        # Remove punctuation and numbers
        if self.config.remove_punctuation:
            text = re.sub(r'[^a-zA-Z\s]', '', text)
            steps.append("remove_punctuation")
            
        # Remove extra whitespace
        if self.config.remove_extra_whitespace:
            text = re.sub(r'\s+', ' ', text).strip()
            steps.append("remove_extra_whitespace")
            
        # Tokenize and process
        tokens = text.split()
        
        # Remove stopwords
        if self.config.remove_stopwords:
            tokens = [token for token in tokens if token not in self.stop_words]
            steps.append("remove_stopwords")
            
        # Filter by length
        tokens = [token for token in tokens 
                 if self.config.min_word_length <= len(token) <= self.config.max_word_length]
        
        return " ".join(tokens)
    
    def _advanced_normalize(self, text: str) -> str:
        """Advanced normalization using spaCy."""
        if not self.nlp:
            return self._basic_normalize(text)
            
        # Process with spaCy
        doc = self.nlp(text)
        
        tokens = []
        for token in doc:
            # Skip if token is space
            if token.is_space:
                continue
                
            # Apply filters
            if self.config.remove_stopwords and token.is_stop:
                continue
            if self.config.remove_punctuation and token.is_punct:
                continue
            if token.is_digit and self.config.remove_numbers:
                continue
            if len(token.text) < self.config.min_word_length:
                continue
            if len(token.text) > self.config.max_word_length:
                continue
                
            # Apply lemmatization
            if self.config.lemmatize:
                token_text = token.lemma_
            else:
                token_text = token.text
                
            # Lowercase
            if self.config.lowercase:
                token_text = token_text.lower()
                
            tokens.append(token_text)
            
        return " ".join(tokens)
    
    def _transformer_normalize(self, text: str) -> str:
        """Normalization using transformer-based tokenization."""
        try:
            # Use a lightweight transformer tokenizer
            tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
            
            # Tokenize
            tokens = tokenizer.tokenize(text)
            
            # Filter tokens
            filtered_tokens = []
            for token in tokens:
                # Remove special tokens
                if token.startswith('##'):
                    token = token[2:]
                if token in ['[CLS]', '[SEP]', '[PAD]', '[UNK]']:
                    continue
                    
                # Apply length filters
                if self.config.min_word_length <= len(token) <= self.config.max_word_length:
                    filtered_tokens.append(token)
                    
            return " ".join(filtered_tokens)
            
        except Exception as e:
            logger.warning(f"Transformer normalization failed: {e}")
            return self._advanced_normalize(text)
    
    def _custom_normalize(self, text: str) -> str:
        """Custom normalization based on configuration."""
        # Unicode normalization
        if self.config.normalize_unicode:
            text = unicodedata.normalize('NFKD', text)
            
        # Remove emojis
        if self.config.remove_emojis:
            text = emoji.replace_emoji(text, replace='')
            
        # Apply basic normalization
        return self._basic_normalize(text)
    
    def batch_normalize(self, texts: List[str], method: NormalizationMethod = NormalizationMethod.ADVANCED) -> List[Dict[str, Any]]:
        """Normalize multiple texts in batch."""
        return [self.normalize(text, method) for text in texts]
    
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
    """Demo the modern text normalizer."""
    # Sample texts for testing
    sample_texts = [
        "Running, jumping, and swimming are fun activities! But are they productive?",
        "I can't believe it's already 2024! 🎉 Check out https://example.com for more info.",
        "The quick brown fox jumps over the lazy dog. It's amazing!",
        "Email me at john.doe@example.com or call (555) 123-4567.",
        "This is a test with EMOJIS 🚀 and special characters: àáâãäåæçèéêë"
    ]
    
    # Initialize normalizer
    config = NormalizationConfig(
        remove_emojis=True,
        remove_urls=True,
        remove_emails=True,
        expand_contractions=True
    )
    normalizer = ModernTextNormalizer(config)
    
    print("🧠 Modern Text Normalization Toolkit Demo")
    print("=" * 50)
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\n📝 Sample {i}:")
        print(f"Original: {text}")
        
        # Test different methods
        for method in NormalizationMethod:
            result = normalizer.normalize(text, method)
            print(f"{method.value.title()}: {result['normalized_text']}")
            
        # Get quality metrics
        metrics = normalizer.get_text_quality_metrics(text)
        print(f"Quality metrics: {metrics}")


if __name__ == "__main__":
    main()
