"""
Setup script for Text Normalization Toolkit
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    # Install basic requirements
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        return False
    
    # Install spaCy model
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy model"):
        print("⚠️ spaCy model download failed, but continuing...")
    
    return True


def setup_database():
    """Initialize the database."""
    print("🗄️ Setting up database...")
    try:
        from database import MockDatabase
        db = MockDatabase()
        stats = db.get_statistics()
        print(f"✅ Database initialized with {stats['total_texts']} texts")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    if not run_command("pytest test_normalizer.py -v", "Running test suite"):
        print("⚠️ Some tests failed, but continuing...")
        return True
    return True


def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    directories = ["logs", "data", "exports"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True


def create_env_file():
    """Create environment configuration file."""
    print("⚙️ Creating environment configuration...")
    
    env_content = """# Text Normalization Toolkit Environment Configuration

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# UI Configuration
UI_PORT=8501
UI_THEME=light

# Database Configuration
DATABASE_PATH=text_normalization.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/normalizer.log

# Model Configuration
SPACY_MODEL=en_core_web_sm
TRANSFORMER_MODEL=distilbert-base-uncased

# Performance Configuration
BATCH_SIZE=100
MAX_TEXT_LENGTH=10000
CACHE_SIZE=1000
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Environment configuration created")
        return True
    except Exception as e:
        print(f"❌ Failed to create environment file: {e}")
        return False


def create_startup_scripts():
    """Create startup scripts."""
    print("🚀 Creating startup scripts...")
    
    # API startup script
    api_script = """#!/bin/bash
# Start the Text Normalization API

echo "🚀 Starting Text Normalization API..."
echo "API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"

python api.py
"""
    
    # UI startup script
    ui_script = """#!/bin/bash
# Start the Text Normalization UI

echo "🎨 Starting Text Normalization UI..."
echo "UI will be available at: http://localhost:8501"
echo "Press Ctrl+C to stop"

streamlit run ui.py
"""
    
    # Test script
    test_script = """#!/bin/bash
# Run the test suite

echo "🧪 Running Text Normalization Tests..."
pytest test_normalizer.py -v --cov=core_normalizer --cov-report=html
echo "Coverage report generated in htmlcov/"
"""
    
    scripts = {
        "start_api.sh": api_script,
        "start_ui.sh": ui_script,
        "run_tests.sh": test_script
    }
    
    for filename, content in scripts.items():
        try:
            with open(filename, "w") as f:
                f.write(content)
            # Make executable on Unix systems
            if os.name != 'nt':
                os.chmod(filename, 0o755)
            print(f"✅ Created startup script: {filename}")
        except Exception as e:
            print(f"❌ Failed to create {filename}: {e}")
            return False
    
    return True


def main():
    """Main setup function."""
    print("🧠 Text Normalization Toolkit Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("❌ Setup failed during database initialization")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("⚠️ Some tests failed, but setup continues...")
    
    # Create environment file
    if not create_env_file():
        print("⚠️ Failed to create environment file, but setup continues...")
    
    # Create startup scripts
    if not create_startup_scripts():
        print("⚠️ Failed to create startup scripts, but setup continues...")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the API: python api.py")
    print("2. Start the UI: streamlit run ui.py")
    print("3. Run tests: pytest test_normalizer.py -v")
    print("4. Check the README.md for detailed usage instructions")
    
    print("\n🌐 Access points:")
    print("- API: http://localhost:8000")
    print("- API Docs: http://localhost:8000/docs")
    print("- UI: http://localhost:8501")
    
    print("\n📚 Documentation:")
    print("- README.md: Complete usage guide")
    print("- API Docs: Interactive API documentation")
    print("- Test Examples: test_normalizer.py")


if __name__ == "__main__":
    main()
