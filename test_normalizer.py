"""
Comprehensive Test Suite for Text Normalization Toolkit
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
import json

from core_normalizer import (
    ModernTextNormalizer, 
    NormalizationConfig, 
    NormalizationMethod
)
from database import MockDatabase


class TestNormalizationConfig:
    """Test NormalizationConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = NormalizationConfig()
        
        assert config.lowercase is True
        assert config.remove_punctuation is True
        assert config.remove_numbers is True
        assert config.remove_stopwords is True
        assert config.lemmatize is True
        assert config.stem is False
        assert config.language == "en"
        assert config.min_word_length == 2
        assert config.max_word_length == 50
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = NormalizationConfig(
            lowercase=False,
            remove_punctuation=False,
            remove_stopwords=False,
            language="es",
            min_word_length=3,
            max_word_length=20
        )
        
        assert config.lowercase is False
        assert config.remove_punctuation is False
        assert config.remove_stopwords is False
        assert config.language == "es"
        assert config.min_word_length == 3
        assert config.max_word_length == 20


class TestModernTextNormalizer:
    """Test ModernTextNormalizer class."""
    
    @pytest.fixture
    def normalizer(self):
        """Create a normalizer instance for testing."""
        return ModernTextNormalizer()
    
    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing."""
        return {
            "basic": "The quick brown fox jumps over the lazy dog.",
            "with_punctuation": "Hello, world! How are you today?",
            "with_numbers": "I have 5 apples and 10 oranges.",
            "with_urls": "Visit https://example.com for more info.",
            "with_emails": "Email me at test@example.com",
            "with_contractions": "I can't believe it's already Friday!",
            "with_emojis": "I love programming! 🚀",
            "mixed_case": "ThIs Is A tExT wItH mIxEd CaSe.",
            "extra_whitespace": "This    text    has    extra    spaces.",
            "empty": "",
            "whitespace_only": "   \n\t   "
        }
    
    def test_normalizer_initialization(self, normalizer):
        """Test normalizer initialization."""
        assert normalizer is not None
        assert normalizer.config is not None
        assert isinstance(normalizer.config, NormalizationConfig)
    
    def test_normalize_basic_text(self, normalizer, sample_texts):
        """Test basic text normalization."""
        text = sample_texts["basic"]
        result = normalizer.normalize(text, NormalizationMethod.BASIC)
        
        assert "normalized_text" in result
        assert "metadata" in result
        assert isinstance(result["normalized_text"], str)
        assert isinstance(result["metadata"], dict)
        assert result["metadata"]["method"] == "basic"
    
    def test_normalize_with_punctuation(self, normalizer, sample_texts):
        """Test normalization with punctuation removal."""
        text = sample_texts["with_punctuation"]
        result = normalizer.normalize(text, NormalizationMethod.BASIC)
        
        # Should remove punctuation
        normalized = result["normalized_text"]
        assert "!" not in normalized
        assert "," not in normalized
        assert "?" not in normalized
    
    def test_normalize_with_numbers(self, normalizer, sample_texts):
        """Test normalization with number removal."""
        text = sample_texts["with_numbers"]
        result = normalizer.normalize(text, NormalizationMethod.BASIC)
        
        # Should remove numbers
        normalized = result["normalized_text"]
        assert "5" not in normalized
        assert "10" not in normalized
    
    def test_normalize_with_urls(self, normalizer, sample_texts):
        """Test normalization with URL removal."""
        text = sample_texts["with_urls"]
        result = normalizer.normalize(text, NormalizationMethod.BASIC)
        
        # Should remove URLs
        normalized = result["normalized_text"]
        assert "https://example.com" not in normalized
    
    def test_normalize_with_emails(self, normalizer, sample_texts):
        """Test normalization with email removal."""
        text = sample_texts["with_emails"]
        result = normalizer.normalize(text, NormalizationMethod.BASIC)
        
        # Should remove emails
        normalized = result["normalized_text"]
        assert "test@example.com" not in normalized
    
    def test_normalize_with_contractions(self, normalizer, sample_texts):
        """Test normalization with contraction expansion."""
        text = sample_texts["with_contractions"]
        result = normalizer.normalize(text, NormalizationMethod.BASIC)
        
        # Should expand contractions
        normalized = result["normalized_text"]
        assert "can't" not in normalized or "cannot" in normalized
        assert "it's" not in normalized or "it is" in normalized
    
    def test_normalize_empty_text(self, normalizer, sample_texts):
        """Test normalization of empty text."""
        text = sample_texts["empty"]
        result = normalizer.normalize(text, NormalizationMethod.BASIC)
        
        assert result["normalized_text"] == ""
        assert "error" in result["metadata"]
    
    def test_normalize_whitespace_only(self, normalizer, sample_texts):
        """Test normalization of whitespace-only text."""
        text = sample_texts["whitespace_only"]
        result = normalizer.normalize(text, NormalizationMethod.BASIC)
        
        assert result["normalized_text"] == ""
    
    def test_normalize_invalid_input(self, normalizer):
        """Test normalization with invalid input."""
        # Test with None
        result = normalizer.normalize(None, NormalizationMethod.BASIC)
        assert result["normalized_text"] == ""
        assert "error" in result["metadata"]
        
        # Test with non-string
        result = normalizer.normalize(123, NormalizationMethod.BASIC)
        assert result["normalized_text"] == ""
        assert "error" in result["metadata"]
    
    def test_batch_normalize(self, normalizer, sample_texts):
        """Test batch normalization."""
        texts = [
            sample_texts["basic"],
            sample_texts["with_punctuation"],
            sample_texts["with_numbers"]
        ]
        
        results = normalizer.batch_normalize(texts, NormalizationMethod.BASIC)
        
        assert len(results) == 3
        for result in results:
            assert "normalized_text" in result
            assert "metadata" in result
    
    def test_get_text_quality_metrics(self, normalizer, sample_texts):
        """Test text quality metrics calculation."""
        text = sample_texts["basic"]
        metrics = normalizer.get_text_quality_metrics(text)
        
        assert isinstance(metrics, dict)
        assert "length" in metrics
        assert "word_count" in metrics
        assert "avg_word_length" in metrics
        assert "punctuation_ratio" in metrics
        assert "uppercase_ratio" in metrics
        assert "digit_ratio" in metrics
        assert "whitespace_ratio" in metrics
        
        # Test with empty text
        empty_metrics = normalizer.get_text_quality_metrics("")
        assert empty_metrics == {}
    
    def test_different_normalization_methods(self, normalizer, sample_texts):
        """Test different normalization methods."""
        text = sample_texts["basic"]
        
        for method in NormalizationMethod:
            result = normalizer.normalize(text, method)
            assert "normalized_text" in result
            assert "metadata" in result
            assert result["metadata"]["method"] == method.value
    
    def test_custom_config(self, sample_texts):
        """Test normalizer with custom configuration."""
        config = NormalizationConfig(
            lowercase=False,
            remove_punctuation=False,
            remove_stopwords=False
        )
        
        normalizer = ModernTextNormalizer(config)
        text = sample_texts["basic"]
        result = normalizer.normalize(text, NormalizationMethod.BASIC)
        
        # Should preserve case and punctuation
        normalized = result["normalized_text"]
        assert any(c.isupper() for c in normalized)  # Should have uppercase
        assert any(c in normalized for c in ".,!?")  # Should have punctuation
    
    @patch('core_normalizer.spacy.load')
    def test_spacy_model_not_found(self, mock_spacy_load, sample_texts):
        """Test behavior when spaCy model is not found."""
        mock_spacy_load.side_effect = OSError("Model not found")
        
        normalizer = ModernTextNormalizer()
        text = sample_texts["basic"]
        result = normalizer.normalize(text, NormalizationMethod.ADVANCED)
        
        # Should fall back to basic normalization
        assert "normalized_text" in result
        assert result["normalized_text"] != ""
    
    @patch('core_normalizer.AutoTokenizer.from_pretrained')
    def test_transformer_tokenizer_failure(self, mock_tokenizer, sample_texts):
        """Test behavior when transformer tokenizer fails."""
        mock_tokenizer.side_effect = Exception("Tokenizer failed")
        
        normalizer = ModernTextNormalizer()
        text = sample_texts["basic"]
        result = normalizer.normalize(text, NormalizationMethod.TRANSFORMER)
        
        # Should fall back to advanced normalization
        assert "normalized_text" in result
        assert result["normalized_text"] != ""


class TestMockDatabase:
    """Test MockDatabase class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = MockDatabase(db_path)
        yield db
        
        # Cleanup
        os.unlink(db_path)
    
    def test_database_initialization(self, temp_db):
        """Test database initialization."""
        assert temp_db is not None
        assert os.path.exists(temp_db.db_path)
    
    def test_get_texts(self, temp_db):
        """Test getting texts from database."""
        texts = temp_db.get_texts()
        
        assert isinstance(texts, list)
        assert len(texts) > 0
        
        for text in texts:
            assert "id" in text
            assert "original_text" in text
            assert "category" in text
            assert "created_at" in text
    
    def test_get_texts_by_category(self, temp_db):
        """Test getting texts by category."""
        categories = temp_db.get_categories()
        assert len(categories) > 0
        
        for category in categories:
            texts = temp_db.get_texts(category=category)
            assert isinstance(texts, list)
            
            for text in texts:
                assert text["category"] == category
    
    def test_get_normalizations(self, temp_db):
        """Test getting normalizations from database."""
        normalizations = temp_db.get_normalizations()
        
        assert isinstance(normalizations, list)
        assert len(normalizations) > 0
        
        for norm in normalizations:
            assert "id" in norm
            assert "text_id" in norm
            assert "method" in norm
            assert "normalized_text" in norm
            assert "metadata" in norm
            assert "created_at" in norm
    
    def test_get_normalizations_by_method(self, temp_db):
        """Test getting normalizations by method."""
        methods = ["basic", "advanced", "transformer", "custom"]
        
        for method in methods:
            normalizations = temp_db.get_normalizations(method=method)
            assert isinstance(normalizations, list)
            
            for norm in normalizations:
                assert norm["method"] == method
    
    def test_get_quality_metrics(self, temp_db):
        """Test getting quality metrics from database."""
        metrics = temp_db.get_quality_metrics()
        
        assert isinstance(metrics, list)
        assert len(metrics) > 0
        
        for metric in metrics:
            assert "id" in metric
            assert "text_id" in metric
            assert "metrics" in metric
            assert "created_at" in metric
    
    def test_get_categories(self, temp_db):
        """Test getting categories."""
        categories = temp_db.get_categories()
        
        assert isinstance(categories, list)
        assert len(categories) > 0
        
        # Check that categories are unique
        assert len(categories) == len(set(categories))
    
    def test_get_statistics(self, temp_db):
        """Test getting database statistics."""
        stats = temp_db.get_statistics()
        
        assert isinstance(stats, dict)
        assert "total_texts" in stats
        assert "total_normalizations" in stats
        assert "total_categories" in stats
        assert "total_methods" in stats
        assert "average_text_length" in stats
        
        assert stats["total_texts"] > 0
        assert stats["total_normalizations"] > 0
        assert stats["total_categories"] > 0
        assert stats["total_methods"] > 0
    
    def test_add_text(self, temp_db):
        """Test adding a new text to database."""
        new_text = "This is a test text for the database."
        text_id = temp_db.add_text(new_text, "test")
        
        assert isinstance(text_id, int)
        assert text_id > 0
        
        # Verify the text was added
        texts = temp_db.get_texts()
        text_ids = [text["id"] for text in texts]
        assert text_id in text_ids
    
    def test_add_normalization(self, temp_db):
        """Test adding a normalization result."""
        # First add a text
        text_id = temp_db.add_text("Test text", "test")
        
        # Add normalization
        metadata = {"test": "data"}
        norm_id = temp_db.add_normalization(
            text_id, "test_method", "test normalized", metadata
        )
        
        assert isinstance(norm_id, int)
        assert norm_id > 0
        
        # Verify the normalization was added
        normalizations = temp_db.get_normalizations(text_id=text_id)
        norm_ids = [norm["id"] for norm in normalizations]
        assert norm_id in norm_ids


class TestIntegration:
    """Integration tests."""
    
    def test_end_to_end_normalization(self):
        """Test end-to-end normalization workflow."""
        # Initialize components
        config = NormalizationConfig(
            remove_emojis=True,
            remove_urls=True,
            remove_emails=True
        )
        normalizer = ModernTextNormalizer(config)
        
        # Test text with various elements
        test_text = "I can't believe it's 2024! 🎉 Email me at test@example.com or visit https://example.com"
        
        # Normalize with different methods
        for method in NormalizationMethod:
            result = normalizer.normalize(test_text, method)
            
            assert "normalized_text" in result
            assert "metadata" in result
            assert result["normalized_text"] != ""
            
            # Should remove URLs and emails
            normalized = result["normalized_text"]
            assert "test@example.com" not in normalized
            assert "https://example.com" not in normalized
    
    def test_database_integration(self):
        """Test database integration with normalizer."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # Initialize database
            db = MockDatabase(db_path)
            
            # Get a sample text
            texts = db.get_texts(limit=1)
            assert len(texts) > 0
            
            text = texts[0]
            
            # Get normalizations for this text
            normalizations = db.get_normalizations(text_id=text["id"])
            assert len(normalizations) > 0
            
            # Verify normalization quality
            for norm in normalizations:
                assert norm["normalized_text"] != ""
                assert norm["method"] in ["basic", "advanced", "transformer", "custom"]
                
                # Parse metadata
                metadata = norm["metadata"]
                assert isinstance(metadata, dict)
                
        finally:
            # Cleanup
            os.unlink(db_path)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
