"""
Mock Database for Text Normalization Toolkit
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import random
from pathlib import Path

from core_normalizer import ModernTextNormalizer, NormalizationConfig, NormalizationMethod


class MockDatabase:
    """Mock database for storing text normalization data."""
    
    def __init__(self, db_path: str = "text_normalization.db"):
        """Initialize the database."""
        self.db_path = db_path
        self.init_database()
        self.populate_sample_data()
    
    def init_database(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS texts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT NOT NULL,
                category TEXT,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS normalizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text_id INTEGER,
                method TEXT NOT NULL,
                config TEXT,
                normalized_text TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (text_id) REFERENCES texts (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text_id INTEGER,
                metrics TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (text_id) REFERENCES texts (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def populate_sample_data(self):
        """Populate database with sample data."""
        sample_texts = [
            {
                "text": "Running, jumping, and swimming are fun activities! But are they productive?",
                "category": "sports"
            },
            {
                "text": "I can't believe it's already 2024! 🎉 Check out https://example.com for more info.",
                "category": "general"
            },
            {
                "text": "The quick brown fox jumps over the lazy dog. It's amazing!",
                "category": "literature"
            },
            {
                "text": "Email me at john.doe@example.com or call (555) 123-4567.",
                "category": "contact"
            },
            {
                "text": "This is a test with EMOJIS 🚀 and special characters: àáâãäåæçèéêë",
                "category": "test"
            },
            {
                "text": "Machine learning algorithms are revolutionizing the way we process data.",
                "category": "technology"
            },
            {
                "text": "The weather today is sunny with a temperature of 75°F. Perfect for outdoor activities!",
                "category": "weather"
            },
            {
                "text": "Café, naïve, résumé - words with accents and special characters.",
                "category": "language"
            },
            {
                "text": "I love programming! 🚀 It's so much fun! 😊 #coding #python",
                "category": "social"
            },
            {
                "text": "The company's revenue increased by 25% in Q3 2024, reaching $2.5M.",
                "category": "business"
            },
            {
                "text": "ThIs Is A tExT wItH mIxEd CaSe AnD eXtRa   sPaCeS.",
                "category": "formatting"
            },
            {
                "text": "Scientists discovered a new species of butterfly in the Amazon rainforest.",
                "category": "science"
            },
            {
                "text": "Don't forget to buy milk, eggs, and bread from the grocery store!",
                "category": "shopping"
            },
            {
                "text": "The movie was absolutely fantastic! I'd rate it 9/10. Highly recommended!",
                "category": "entertainment"
            },
            {
                "text": "COVID-19 vaccination rates have reached 85% in our community.",
                "category": "health"
            }
        ]
        
        # Insert sample texts
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for text_data in sample_texts:
            cursor.execute("""
                INSERT OR IGNORE INTO texts (original_text, category)
                VALUES (?, ?)
            """, (text_data["text"], text_data["category"]))
        
        conn.commit()
        conn.close()
        
        # Generate normalization results for sample texts
        self.generate_sample_normalizations()
    
    def generate_sample_normalizations(self):
        """Generate sample normalization results."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all texts
        cursor.execute("SELECT id, original_text FROM texts")
        texts = cursor.fetchall()
        
        # Initialize normalizer
        normalizer = ModernTextNormalizer()
        
        # Generate normalizations for each method
        for text_id, original_text in texts:
            for method in NormalizationMethod:
                try:
                    result = normalizer.normalize(original_text, method)
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO normalizations 
                        (text_id, method, normalized_text, metadata)
                        VALUES (?, ?, ?, ?)
                    """, (
                        text_id,
                        method.value,
                        result["normalized_text"],
                        json.dumps(result["metadata"])
                    ))
                    
                    # Generate quality metrics
                    metrics = normalizer.get_text_quality_metrics(original_text)
                    cursor.execute("""
                        INSERT OR IGNORE INTO quality_metrics (text_id, metrics)
                        VALUES (?, ?)
                    """, (text_id, json.dumps(metrics)))
                    
                except Exception as e:
                    print(f"Error processing text {text_id} with method {method}: {e}")
        
        conn.commit()
        conn.close()
    
    def get_texts(self, category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get texts from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT id, original_text, category, created_at 
                FROM texts 
                WHERE category = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (category, limit))
        else:
            cursor.execute("""
                SELECT id, original_text, category, created_at 
                FROM texts 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
        
        texts = []
        for row in cursor.fetchall():
            texts.append({
                "id": row[0],
                "original_text": row[1],
                "category": row[2],
                "created_at": row[3]
            })
        
        conn.close()
        return texts
    
    def get_normalizations(self, text_id: Optional[int] = None, method: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get normalization results."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if text_id and method:
            cursor.execute("""
                SELECT n.id, n.text_id, n.method, n.normalized_text, n.metadata, n.created_at,
                       t.original_text, t.category
                FROM normalizations n
                JOIN texts t ON n.text_id = t.id
                WHERE n.text_id = ? AND n.method = ?
                ORDER BY n.created_at DESC
            """, (text_id, method))
        elif text_id:
            cursor.execute("""
                SELECT n.id, n.text_id, n.method, n.normalized_text, n.metadata, n.created_at,
                       t.original_text, t.category
                FROM normalizations n
                JOIN texts t ON n.text_id = t.id
                WHERE n.text_id = ?
                ORDER BY n.created_at DESC
            """, (text_id,))
        elif method:
            cursor.execute("""
                SELECT n.id, n.text_id, n.method, n.normalized_text, n.metadata, n.created_at,
                       t.original_text, t.category
                FROM normalizations n
                JOIN texts t ON n.text_id = t.id
                WHERE n.method = ?
                ORDER BY n.created_at DESC
            """, (method,))
        else:
            cursor.execute("""
                SELECT n.id, n.text_id, n.method, n.normalized_text, n.metadata, n.created_at,
                       t.original_text, t.category
                FROM normalizations n
                JOIN texts t ON n.text_id = t.id
                ORDER BY n.created_at DESC
            """)
        
        normalizations = []
        for row in cursor.fetchall():
            normalizations.append({
                "id": row[0],
                "text_id": row[1],
                "method": row[2],
                "normalized_text": row[3],
                "metadata": json.loads(row[4]) if row[4] else {},
                "created_at": row[5],
                "original_text": row[6],
                "category": row[7]
            })
        
        conn.close()
        return normalizations
    
    def get_quality_metrics(self, text_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get quality metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if text_id:
            cursor.execute("""
                SELECT q.id, q.text_id, q.metrics, q.created_at, t.original_text, t.category
                FROM quality_metrics q
                JOIN texts t ON q.text_id = t.id
                WHERE q.text_id = ?
                ORDER BY q.created_at DESC
            """, (text_id,))
        else:
            cursor.execute("""
                SELECT q.id, q.text_id, q.metrics, q.created_at, t.original_text, t.category
                FROM quality_metrics q
                JOIN texts t ON q.text_id = t.id
                ORDER BY q.created_at DESC
            """)
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                "id": row[0],
                "text_id": row[1],
                "metrics": json.loads(row[2]) if row[2] else {},
                "created_at": row[3],
                "original_text": row[4],
                "category": row[5]
            })
        
        conn.close()
        return metrics
    
    def get_categories(self) -> List[str]:
        """Get all categories."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT category FROM texts ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return categories
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count texts
        cursor.execute("SELECT COUNT(*) FROM texts")
        text_count = cursor.fetchone()[0]
        
        # Count normalizations
        cursor.execute("SELECT COUNT(*) FROM normalizations")
        normalization_count = cursor.fetchone()[0]
        
        # Count categories
        cursor.execute("SELECT COUNT(DISTINCT category) FROM texts")
        category_count = cursor.fetchone()[0]
        
        # Count methods
        cursor.execute("SELECT COUNT(DISTINCT method) FROM normalizations")
        method_count = cursor.fetchone()[0]
        
        # Average text length
        cursor.execute("SELECT AVG(LENGTH(original_text)) FROM texts")
        avg_length = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_texts": text_count,
            "total_normalizations": normalization_count,
            "total_categories": category_count,
            "total_methods": method_count,
            "average_text_length": round(avg_length, 2)
        }
    
    def add_text(self, text: str, category: str = "general") -> int:
        """Add a new text to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO texts (original_text, category)
            VALUES (?, ?)
        """, (text, category))
        
        text_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return text_id
    
    def add_normalization(self, text_id: int, method: str, normalized_text: str, metadata: Dict[str, Any]) -> int:
        """Add a normalization result."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO normalizations (text_id, method, normalized_text, metadata)
            VALUES (?, ?, ?, ?)
        """, (text_id, method, normalized_text, json.dumps(metadata)))
        
        norm_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return norm_id


def main():
    """Demo the mock database."""
    print("🗄️ Mock Database Demo")
    print("=" * 50)
    
    # Initialize database
    db = MockDatabase()
    
    # Get statistics
    stats = db.get_statistics()
    print(f"📊 Database Statistics:")
    print(f"  Total texts: {stats['total_texts']}")
    print(f"  Total normalizations: {stats['total_normalizations']}")
    print(f"  Categories: {stats['total_categories']}")
    print(f"  Methods: {stats['total_methods']}")
    print(f"  Average text length: {stats['average_text_length']}")
    
    # Get categories
    categories = db.get_categories()
    print(f"\n📂 Categories: {', '.join(categories)}")
    
    # Get sample texts
    print(f"\n📝 Sample Texts:")
    texts = db.get_texts(limit=3)
    for text in texts:
        print(f"  [{text['category']}] {text['original_text'][:50]}...")
    
    # Get normalizations for first text
    if texts:
        first_text = texts[0]
        print(f"\n✨ Normalizations for '{first_text['original_text'][:30]}...':")
        
        normalizations = db.get_normalizations(text_id=first_text['id'])
        for norm in normalizations:
            print(f"  [{norm['method']}] {norm['normalized_text']}")
    
    # Get quality metrics
    if texts:
        first_text = texts[0]
        print(f"\n📊 Quality Metrics:")
        
        metrics = db.get_quality_metrics(text_id=first_text['id'])
        if metrics:
            metric_data = metrics[0]['metrics']
            for key, value in metric_data.items():
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
