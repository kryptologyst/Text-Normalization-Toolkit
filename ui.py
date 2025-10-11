"""
Modern Streamlit UI for Text Normalization Toolkit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import requests
from typing import Dict, List, Any

from core_normalizer import ModernTextNormalizer, NormalizationConfig, NormalizationMethod

# Page configuration
st.set_page_config(
    page_title="Text Normalization Toolkit",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'normalizer' not in st.session_state:
    st.session_state.normalizer = ModernTextNormalizer()

if 'normalization_history' not in st.session_state:
    st.session_state.normalization_history = []


def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">🧠 Text Normalization Toolkit</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Normalization method selection
        method = st.selectbox(
            "Normalization Method",
            options=[method.value for method in NormalizationMethod],
            index=1,  # Default to 'advanced'
            help="Choose the normalization method to use"
        )
        
        st.subheader("🔧 Advanced Settings")
        
        # Configuration options
        config_options = {
            "lowercase": st.checkbox("Convert to lowercase", value=True),
            "remove_punctuation": st.checkbox("Remove punctuation", value=True),
            "remove_numbers": st.checkbox("Remove numbers", value=True),
            "remove_extra_whitespace": st.checkbox("Remove extra whitespace", value=True),
            "remove_stopwords": st.checkbox("Remove stop words", value=True),
            "lemmatize": st.checkbox("Apply lemmatization", value=True),
            "stem": st.checkbox("Apply stemming", value=False),
            "expand_contractions": st.checkbox("Expand contractions", value=True),
            "normalize_unicode": st.checkbox("Normalize Unicode", value=True),
            "remove_emojis": st.checkbox("Remove emojis", value=False),
            "remove_urls": st.checkbox("Remove URLs", value=True),
            "remove_emails": st.checkbox("Remove emails", value=True),
        }
        
        # Word length filters
        col1, col2 = st.columns(2)
        with col1:
            min_length = st.number_input("Min word length", min_value=1, max_value=20, value=2)
        with col2:
            max_length = st.number_input("Max word length", min_value=1, max_value=100, value=50)
        
        config_options["min_word_length"] = min_length
        config_options["max_word_length"] = max_length
        
        # Language selection
        language = st.selectbox("Language", ["en", "es", "fr", "de"], index=0)
        config_options["language"] = language
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Single Text", "📊 Batch Processing", "📈 Analytics", "📚 Examples"])
    
    with tab1:
        single_text_interface(method, config_options)
    
    with tab2:
        batch_processing_interface(method, config_options)
    
    with tab3:
        analytics_interface()
    
    with tab4:
        examples_interface(method, config_options)


def single_text_interface(method: str, config_options: Dict[str, Any]):
    """Single text normalization interface."""
    
    st.header("📝 Single Text Normalization")
    
    # Text input
    text_input = st.text_area(
        "Enter text to normalize:",
        height=150,
        placeholder="Enter your text here...",
        help="Type or paste the text you want to normalize"
    )
    
    if st.button("🚀 Normalize Text", type="primary"):
        if text_input.strip():
            with st.spinner("Normalizing text..."):
                # Create configuration
                config = NormalizationConfig(**config_options)
                normalizer = ModernTextNormalizer(config)
                
                # Normalize text
                method_enum = NormalizationMethod(method)
                result = normalizer.normalize(text_input, method_enum)
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📄 Original Text")
                    st.text_area("", value=text_input, height=100, disabled=True)
                
                with col2:
                    st.subheader("✨ Normalized Text")
                    st.text_area("", value=result["normalized_text"], height=100, disabled=True)
                
                # Metrics
                st.subheader("📊 Text Metrics")
                
                metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                
                with metrics_col1:
                    st.metric("Original Length", len(text_input))
                with metrics_col2:
                    st.metric("Normalized Length", len(result["normalized_text"]))
                with metrics_col3:
                    compression_ratio = result["metadata"].get("compression_ratio", 0)
                    st.metric("Compression Ratio", f"{compression_ratio:.2%}")
                with metrics_col4:
                    word_count = len(result["normalized_text"].split())
                    st.metric("Word Count", word_count)
                
                # Quality metrics
                quality_metrics = normalizer.get_text_quality_metrics(text_input)
                
                st.subheader("🔍 Quality Analysis")
                
                quality_col1, quality_col2, quality_col3, quality_col4 = st.columns(4)
                
                with quality_col1:
                    st.metric("Avg Word Length", f"{quality_metrics.get('avg_word_length', 0):.1f}")
                with quality_col2:
                    st.metric("Punctuation Ratio", f"{quality_metrics.get('punctuation_ratio', 0):.2%}")
                with quality_col3:
                    st.metric("Uppercase Ratio", f"{quality_metrics.get('uppercase_ratio', 0):.2%}")
                with quality_col4:
                    st.metric("Digit Ratio", f"{quality_metrics.get('digit_ratio', 0):.2%}")
                
                # Save to history
                st.session_state.normalization_history.append({
                    "timestamp": datetime.now(),
                    "original_text": text_input,
                    "normalized_text": result["normalized_text"],
                    "method": method,
                    "config": config_options,
                    "metrics": quality_metrics
                })
                
                st.success("✅ Text normalized successfully!")
        else:
            st.warning("⚠️ Please enter some text to normalize.")


def batch_processing_interface(method: str, config_options: Dict[str, Any]):
    """Batch processing interface."""
    
    st.header("📊 Batch Text Processing")
    
    # Input options
    input_option = st.radio(
        "Choose input method:",
        ["Manual Entry", "Upload File", "Sample Data"]
    )
    
    texts = []
    
    if input_option == "Manual Entry":
        st.subheader("📝 Enter Multiple Texts")
        text_input = st.text_area(
            "Enter texts (one per line):",
            height=200,
            placeholder="Text 1\nText 2\nText 3\n...",
            help="Enter multiple texts, one per line"
        )
        
        if text_input.strip():
            texts = [line.strip() for line in text_input.split('\n') if line.strip()]
    
    elif input_option == "Upload File":
        st.subheader("📁 Upload Text File")
        uploaded_file = st.file_uploader(
            "Choose a text file",
            type=['txt', 'csv'],
            help="Upload a text file with one text per line"
        )
        
        if uploaded_file:
            if uploaded_file.type == "text/plain":
                content = uploaded_file.read().decode("utf-8")
                texts = [line.strip() for line in content.split('\n') if line.strip()]
            elif uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
                if 'text' in df.columns:
                    texts = df['text'].astype(str).tolist()
                else:
                    st.error("CSV file must have a 'text' column")
    
    else:  # Sample Data
        st.subheader("🎯 Sample Data")
        sample_texts = [
            "Running, jumping, and swimming are fun activities! But are they productive?",
            "I can't believe it's already 2024! 🎉 Check out https://example.com for more info.",
            "The quick brown fox jumps over the lazy dog. It's amazing!",
            "Email me at john.doe@example.com or call (555) 123-4567.",
            "This is a test with EMOJIS 🚀 and special characters: àáâãäåæçèéêë"
        ]
        
        texts = sample_texts
        st.info(f"Using {len(sample_texts)} sample texts")
    
    if texts and st.button("🚀 Process Batch", type="primary"):
        with st.spinner(f"Processing {len(texts)} texts..."):
            # Create configuration
            config = NormalizationConfig(**config_options)
            normalizer = ModernTextNormalizer(config)
            
            # Process texts
            method_enum = NormalizationMethod(method)
            results = normalizer.batch_normalize(texts, method_enum)
            
            # Create results DataFrame
            df_results = pd.DataFrame([
                {
                    "Original": result["normalized_text"],
                    "Normalized": result["normalized_text"],
                    "Original Length": result["metadata"]["original_length"],
                    "Final Length": result["metadata"]["final_length"],
                    "Compression Ratio": result["metadata"].get("compression_ratio", 0)
                }
                for result in results
            ])
            
            # Display results
            st.subheader("📊 Batch Processing Results")
            st.dataframe(df_results, use_container_width=True)
            
            # Summary statistics
            st.subheader("📈 Summary Statistics")
            
            summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
            
            with summary_col1:
                st.metric("Total Texts", len(texts))
            with summary_col2:
                avg_compression = df_results["Compression Ratio"].mean()
                st.metric("Avg Compression", f"{avg_compression:.2%}")
            with summary_col3:
                avg_original_length = df_results["Original Length"].mean()
                st.metric("Avg Original Length", f"{avg_original_length:.1f}")
            with summary_col4:
                avg_final_length = df_results["Final Length"].mean()
                st.metric("Avg Final Length", f"{avg_final_length:.1f}")
            
            # Visualization
            st.subheader("📊 Compression Ratio Distribution")
            
            fig = px.histogram(
                df_results,
                x="Compression Ratio",
                nbins=20,
                title="Distribution of Compression Ratios",
                labels={"Compression Ratio": "Compression Ratio", "count": "Number of Texts"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Download results
            csv = df_results.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"normalization_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


def analytics_interface():
    """Analytics and history interface."""
    
    st.header("📈 Analytics & History")
    
    if not st.session_state.normalization_history:
        st.info("No normalization history available. Process some texts to see analytics here.")
        return
    
    # Convert history to DataFrame
    history_df = pd.DataFrame(st.session_state.normalization_history)
    
    st.subheader("📊 Processing History")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Normalizations", len(history_df))
    with col2:
        unique_methods = history_df["method"].nunique()
        st.metric("Methods Used", unique_methods)
    with col3:
        avg_length = history_df["original_text"].str.len().mean()
        st.metric("Avg Text Length", f"{avg_length:.1f}")
    with col4:
        recent_count = len(history_df[history_df["timestamp"] > datetime.now().replace(hour=0, minute=0, second=0)])
        st.metric("Today's Count", recent_count)
    
    # Method usage chart
    st.subheader("📊 Method Usage")
    method_counts = history_df["method"].value_counts()
    
    fig_methods = px.pie(
        values=method_counts.values,
        names=method_counts.index,
        title="Normalization Method Usage"
    )
    st.plotly_chart(fig_methods, use_container_width=True)
    
    # Text length distribution
    st.subheader("📏 Text Length Distribution")
    
    fig_length = px.histogram(
        history_df,
        x=history_df["original_text"].str.len(),
        nbins=20,
        title="Distribution of Original Text Lengths",
        labels={"x": "Text Length", "count": "Number of Texts"}
    )
    st.plotly_chart(fig_length, use_container_width=True)
    
    # Recent activity
    st.subheader("🕒 Recent Activity")
    
    recent_df = history_df.tail(10)[["timestamp", "method", "original_text"]].copy()
    recent_df["original_text"] = recent_df["original_text"].str[:50] + "..."
    
    st.dataframe(recent_df, use_container_width=True)
    
    # Clear history button
    if st.button("🗑️ Clear History", type="secondary"):
        st.session_state.normalization_history = []
        st.rerun()


def examples_interface(method: str, config_options: Dict[str, Any]):
    """Examples and demos interface."""
    
    st.header("📚 Examples & Demos")
    
    # Example texts with different characteristics
    examples = {
        "Basic Text": "The quick brown fox jumps over the lazy dog.",
        "With Punctuation": "Hello, world! How are you today? I'm doing great!",
        "With Numbers": "I have 5 apples and 10 oranges. The year is 2024.",
        "With URLs & Emails": "Visit https://example.com or email me at test@example.com",
        "With Contractions": "I can't believe it's already Friday! We're going to have fun.",
        "With Emojis": "I love programming! 🚀 It's so much fun! 😊",
        "Mixed Case": "ThIs Is A tExT wItH mIxEd CaSe.",
        "Extra Whitespace": "This    text    has    extra    spaces    everywhere.",
        "Special Characters": "Café, naïve, résumé - words with accents and special characters.",
        "Long Text": "This is a longer text that contains multiple sentences. It demonstrates how the normalization process works with more complex input. The system should handle this gracefully and produce clean, normalized output that maintains the essential meaning while removing unnecessary elements."
    }
    
    st.subheader("🎯 Try Different Text Types")
    
    selected_example = st.selectbox(
        "Choose an example:",
        list(examples.keys())
    )
    
    if selected_example:
        example_text = examples[selected_example]
        
        st.text_area(
            "Example Text:",
            value=example_text,
            height=100,
            disabled=True
        )
        
        if st.button(f"🚀 Normalize '{selected_example}'", type="primary"):
            with st.spinner("Normalizing example text..."):
                # Create configuration
                config = NormalizationConfig(**config_options)
                normalizer = ModernTextNormalizer(config)
                
                # Normalize text
                method_enum = NormalizationMethod(method)
                result = normalizer.normalize(example_text, method_enum)
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📄 Original")
                    st.text_area("", value=example_text, height=100, disabled=True)
                
                with col2:
                    st.subheader("✨ Normalized")
                    st.text_area("", value=result["normalized_text"], height=100, disabled=True)
                
                # Show what changed
                st.subheader("🔍 What Changed")
                
                changes = []
                if len(example_text) != len(result["normalized_text"]):
                    changes.append(f"Length: {len(example_text)} → {len(result['normalized_text'])}")
                
                if example_text.lower() != result["normalized_text"]:
                    changes.append("Case normalization applied")
                
                if any(char in example_text for char in "!@#$%^&*()"):
                    changes.append("Punctuation removed")
                
                if any(word in example_text.lower() for word in ["the", "a", "an", "and", "or", "but"]):
                    changes.append("Stop words removed")
                
                if changes:
                    for change in changes:
                        st.write(f"• {change}")
                else:
                    st.write("• No significant changes detected")
    
    # Method comparison
    st.subheader("🔄 Method Comparison")
    
    comparison_text = st.text_area(
        "Enter text to compare methods:",
        value="Running, jumping, and swimming are fun activities! But are they productive?",
        height=100
    )
    
    if st.button("🔄 Compare All Methods", type="primary"):
        if comparison_text.strip():
            with st.spinner("Comparing normalization methods..."):
                config = NormalizationConfig(**config_options)
                normalizer = ModernTextNormalizer(config)
                
                comparison_results = []
                
                for method_enum in NormalizationMethod:
                    result = normalizer.normalize(comparison_text, method_enum)
                    comparison_results.append({
                        "Method": method_enum.value.title(),
                        "Result": result["normalized_text"],
                        "Length": len(result["normalized_text"]),
                        "Compression": f"{result['metadata'].get('compression_ratio', 0):.2%}"
                    })
                
                comparison_df = pd.DataFrame(comparison_results)
                st.dataframe(comparison_df, use_container_width=True)
        else:
            st.warning("⚠️ Please enter some text to compare.")


if __name__ == "__main__":
    main()
