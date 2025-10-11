"""
FastAPI REST API for Text Normalization Service
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import logging
from datetime import datetime

from core_normalizer import ModernTextNormalizer, NormalizationConfig, NormalizationMethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Text Normalization API",
    description="A modern API for text normalization using advanced NLP techniques",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize normalizer
normalizer = ModernTextNormalizer()


# Pydantic models
class TextNormalizationRequest(BaseModel):
    text: str = Field(..., description="Text to normalize", min_length=1)
    method: str = Field("advanced", description="Normalization method")
    config: Optional[Dict[str, Any]] = Field(None, description="Custom configuration")


class BatchNormalizationRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to normalize", min_items=1)
    method: str = Field("advanced", description="Normalization method")
    config: Optional[Dict[str, Any]] = Field(None, description="Custom configuration")


class TextQualityRequest(BaseModel):
    text: str = Field(..., description="Text to analyze", min_length=1)


class NormalizationResponse(BaseModel):
    normalized_text: str
    metadata: Dict[str, Any]
    timestamp: datetime


class BatchNormalizationResponse(BaseModel):
    results: List[NormalizationResponse]
    total_processed: int
    timestamp: datetime


class QualityMetricsResponse(BaseModel):
    metrics: Dict[str, Any]
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str


# Helper functions
def get_normalization_method(method_str: str) -> NormalizationMethod:
    """Convert string to NormalizationMethod enum."""
    method_map = {
        "basic": NormalizationMethod.BASIC,
        "advanced": NormalizationMethod.ADVANCED,
        "transformer": NormalizationMethod.TRANSFORMER,
        "custom": NormalizationMethod.CUSTOM
    }
    
    if method_str.lower() not in method_map:
        raise HTTPException(status_code=400, detail=f"Invalid method. Must be one of: {list(method_map.keys())}")
    
    return method_map[method_str.lower()]


def create_config_from_dict(config_dict: Optional[Dict[str, Any]]) -> NormalizationConfig:
    """Create NormalizationConfig from dictionary."""
    if not config_dict:
        return NormalizationConfig()
    
    return NormalizationConfig(**config_dict)


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.post("/normalize", response_model=NormalizationResponse)
async def normalize_text(request: TextNormalizationRequest):
    """
    Normalize a single text using specified method and configuration.
    """
    try:
        method = get_normalization_method(request.method)
        config = create_config_from_dict(request.config)
        
        # Create normalizer with custom config if provided
        if request.config:
            normalizer_with_config = ModernTextNormalizer(config)
            result = normalizer_with_config.normalize(request.text, method)
        else:
            result = normalizer.normalize(request.text, method)
        
        return NormalizationResponse(
            normalized_text=result["normalized_text"],
            metadata=result["metadata"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Normalization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/normalize/batch", response_model=BatchNormalizationResponse)
async def normalize_texts_batch(request: BatchNormalizationRequest):
    """
    Normalize multiple texts in batch.
    """
    try:
        method = get_normalization_method(request.method)
        config = create_config_from_dict(request.config)
        
        # Create normalizer with custom config if provided
        if request.config:
            normalizer_with_config = ModernTextNormalizer(config)
            results = normalizer_with_config.batch_normalize(request.texts, method)
        else:
            results = normalizer.batch_normalize(request.texts, method)
        
        # Convert to response format
        response_results = [
            NormalizationResponse(
                normalized_text=result["normalized_text"],
                metadata=result["metadata"],
                timestamp=datetime.now()
            )
            for result in results
        ]
        
        return BatchNormalizationResponse(
            results=response_results,
            total_processed=len(response_results),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Batch normalization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/quality", response_model=QualityMetricsResponse)
async def analyze_text_quality(request: TextQualityRequest):
    """
    Analyze text quality metrics.
    """
    try:
        metrics = normalizer.get_text_quality_metrics(request.text)
        
        return QualityMetricsResponse(
            metrics=metrics,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Quality analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/methods")
async def get_available_methods():
    """
    Get list of available normalization methods.
    """
    return {
        "methods": [
            {
                "name": method.value,
                "description": f"{method.value.title()} normalization method"
            }
            for method in NormalizationMethod
        ]
    }


@app.get("/config/schema")
async def get_config_schema():
    """
    Get the configuration schema for custom normalization settings.
    """
    return {
        "schema": {
            "lowercase": {"type": "boolean", "default": True, "description": "Convert text to lowercase"},
            "remove_punctuation": {"type": "boolean", "default": True, "description": "Remove punctuation marks"},
            "remove_numbers": {"type": "boolean", "default": True, "description": "Remove numeric characters"},
            "remove_extra_whitespace": {"type": "boolean", "default": True, "description": "Remove extra whitespace"},
            "remove_stopwords": {"type": "boolean", "default": True, "description": "Remove stop words"},
            "lemmatize": {"type": "boolean", "default": True, "description": "Apply lemmatization"},
            "stem": {"type": "boolean", "default": False, "description": "Apply stemming"},
            "expand_contractions": {"type": "boolean", "default": True, "description": "Expand contractions"},
            "normalize_unicode": {"type": "boolean", "default": True, "description": "Normalize Unicode characters"},
            "remove_emojis": {"type": "boolean", "default": False, "description": "Remove emoji characters"},
            "remove_urls": {"type": "boolean", "default": True, "description": "Remove URLs"},
            "remove_emails": {"type": "boolean", "default": True, "description": "Remove email addresses"},
            "min_word_length": {"type": "integer", "default": 2, "description": "Minimum word length"},
            "max_word_length": {"type": "integer", "default": 50, "description": "Maximum word length"},
            "language": {"type": "string", "default": "en", "description": "Language code"},
            "custom_stopwords": {"type": "array", "default": None, "description": "Custom stop words list"}
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
