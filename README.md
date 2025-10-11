# Text Normalization Toolkit

A comprehensive toolkit for text normalization using the latest NLP techniques and libraries. This toolkit provides advanced text preprocessing capabilities with multiple normalization methods, a REST API, interactive web UI, and comprehensive testing.

## Features

### Core Functionality
- **Multiple Normalization Methods**: Basic, Advanced (spaCy), Transformer-based, and Custom
- **Advanced Text Processing**: Unicode normalization, emoji handling, URL/email detection
- **Configurable Pipeline**: Customizable normalization settings
- **Quality Metrics**: Text quality analysis and evaluation tools
- **Batch Processing**: Process multiple texts efficiently

### Web Interface
- **REST API**: FastAPI-based service with comprehensive endpoints
- **Interactive UI**: Modern Streamlit interface with real-time processing
- **Analytics Dashboard**: Processing history and performance metrics
- **Example Gallery**: Pre-built examples for different text types

### Data Management
- **Mock Database**: SQLite database with sample texts and results
- **Comprehensive Testing**: Full test suite with pytest
- **Documentation**: Detailed API documentation and usage examples

## Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/kryptologyst/Text-Normalization-Toolkit.git
cd Text-Normalization-Toolkit
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Download required models**:
```bash
python -m spacy download en_core_web_sm
```

### Basic Usage

```python
from core_normalizer import ModernTextNormalizer, NormalizationConfig, NormalizationMethod

# Initialize normalizer
normalizer = ModernTextNormalizer()

# Normalize text
text = "Running, jumping, and swimming are fun activities! But are they productive?"
result = normalizer.normalize(text, NormalizationMethod.ADVANCED)

print(f"Original: {text}")
print(f"Normalized: {result['normalized_text']}")
```

### Custom Configuration

```python
# Create custom configuration
config = NormalizationConfig(
    lowercase=True,
    remove_punctuation=True,
    remove_stopwords=True,
    remove_emojis=True,
    remove_urls=True,
    expand_contractions=True,
    min_word_length=2,
    max_word_length=50
)

# Initialize with custom config
normalizer = ModernTextNormalizer(config)
```

## API Documentation

### REST API Endpoints

#### Health Check
```http
GET /health
```

#### Single Text Normalization
```http
POST /normalize
Content-Type: application/json

{
    "text": "Your text here",
    "method": "advanced",
    "config": {
        "remove_emojis": true,
        "remove_urls": true
    }
}
```

#### Batch Processing
```http
POST /normalize/batch
Content-Type: application/json

{
    "texts": ["Text 1", "Text 2", "Text 3"],
    "method": "advanced"
}
```

#### Text Quality Analysis
```http
POST /analyze/quality
Content-Type: application/json

{
    "text": "Your text here"
}
```

#### Available Methods
```http
GET /methods
```

#### Configuration Schema
```http
GET /config/schema
```

### Running the API Server

```bash
# Start the API server
python api.py

# Or with uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Web Interface

### Running the Streamlit UI

```bash
streamlit run ui.py
```

The web interface will be available at `http://localhost:8501`.

### Features
- **Single Text Processing**: Interactive text normalization
- **Batch Processing**: Upload files or enter multiple texts
- **Analytics Dashboard**: Processing history and metrics
- **Example Gallery**: Try different text types and methods
- **Real-time Configuration**: Adjust settings on the fly

## Database

### Mock Database Features
- **Sample Texts**: Pre-loaded with various text categories
- **Normalization Results**: Pre-computed results for all methods
- **Quality Metrics**: Text analysis metrics
- **Statistics**: Database usage statistics

### Using the Database

```python
from database import MockDatabase

# Initialize database
db = MockDatabase()

# Get texts by category
texts = db.get_texts(category="technology")

# Get normalizations
normalizations = db.get_normalizations(method="advanced")

# Get quality metrics
metrics = db.get_quality_metrics()

# Get statistics
stats = db.get_statistics()
```

## Testing

### Running Tests

```bash
# Run all tests
pytest test_normalizer.py -v

# Run with coverage
pytest test_normalizer.py --cov=core_normalizer --cov-report=html

# Run specific test class
pytest test_normalizer.py::TestModernTextNormalizer -v
```

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Mock Testing**: Database and external service mocking
- **Edge Cases**: Empty text, invalid input, error handling

## Normalization Methods

### 1. Basic Method
- Traditional regex-based processing
- Fast and lightweight
- Good for simple text preprocessing

### 2. Advanced Method (spaCy)
- Uses spaCy's linguistic analysis
- Part-of-speech tagging
- Advanced tokenization and lemmatization

### 3. Transformer Method
- Uses transformer-based tokenization
- State-of-the-art NLP processing
- Best for complex text understanding

### 4. Custom Method
- Configurable pipeline
- Unicode normalization
- Emoji handling
- Custom preprocessing rules

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `lowercase` | bool | True | Convert text to lowercase |
| `remove_punctuation` | bool | True | Remove punctuation marks |
| `remove_numbers` | bool | True | Remove numeric characters |
| `remove_extra_whitespace` | bool | True | Remove extra whitespace |
| `remove_stopwords` | bool | True | Remove stop words |
| `lemmatize` | bool | True | Apply lemmatization |
| `stem` | bool | False | Apply stemming |
| `expand_contractions` | bool | True | Expand contractions |
| `normalize_unicode` | bool | True | Normalize Unicode characters |
| `remove_emojis` | bool | False | Remove emoji characters |
| `remove_urls` | bool | True | Remove URLs |
| `remove_emails` | bool | True | Remove email addresses |
| `min_word_length` | int | 2 | Minimum word length |
| `max_word_length` | int | 50 | Maximum word length |
| `language` | str | "en" | Language code |
| `custom_stopwords` | list | None | Custom stop words list |

## Performance Metrics

The toolkit provides comprehensive text quality metrics:

- **Length Metrics**: Original and normalized text lengths
- **Word Analysis**: Word count, average word length
- **Character Analysis**: Punctuation, uppercase, digit ratios
- **Compression Ratio**: Text size reduction percentage
- **Processing Time**: Normalization performance metrics

## 🔧 Development

### Project Structure
```
text-normalization-toolkit/
├── core_normalizer.py      # Core normalization logic
├── api.py                 # FastAPI REST API
├── ui.py                  # Streamlit web interface
├── database.py            # Mock database implementation
├── test_normalizer.py     # Comprehensive test suite
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── 0183.py               # Original implementation
```

### Adding New Features

1. **New Normalization Method**:
   - Add method to `NormalizationMethod` enum
   - Implement method in `ModernTextNormalizer`
   - Add tests for the new method

2. **New Configuration Option**:
   - Add field to `NormalizationConfig`
   - Update normalization logic
   - Add API endpoint for configuration
   - Update UI controls

3. **New Quality Metric**:
   - Add calculation to `get_text_quality_metrics`
   - Update database schema if needed
   - Add visualization in UI

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **spaCy**: Advanced NLP processing
- **NLTK**: Natural language processing toolkit
- **Transformers**: State-of-the-art NLP models
- **FastAPI**: Modern web framework
- **Streamlit**: Interactive web applications
- **SQLite**: Lightweight database

## Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the documentation
- Review the test examples


# Text-Normalization-Toolkit
