"""
Image-to-Word Converter Web App (Streamlit)
A web application that extracts text from images while preserving basic formatting.
Deployed on Streamlit Cloud for easy sharing.
"""

import streamlit as st
import tempfile
import os
from PIL import Image
import io
from image_preprocessor import ImagePreprocessor
from ocr_engine import OCREngine
from formatting_detector import FormattingDetector
from docx_generator import DOCXGenerator


# Page configuration
st.set_page_config(
    page_title="Image to Word Converter",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2c3e50;
        padding: 20px 0;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .preview-section {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 20px 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'converted_docx' not in st.session_state:
        st.session_state.converted_docx = None


def display_image_preview(image_file):
    """Display image preview in the main area"""
    if image_file is not None:
        try:
            image = Image.open(image_file)
            # Resize for display
            max_size = (600, 400)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            st.image(image, caption="Uploaded Image", use_column_width=True)
            return True
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
            return False
    return False


def process_image(image_file, preprocess, detect_formatting, language):
    """Process the uploaded image"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            # Save uploaded image to temporary file
            image = Image.open(image_file)
            image.save(tmp_file.name)
            temp_path = tmp_file.name
        
        # Initialize processors
        preprocessor = ImagePreprocessor()
        ocr_engine = OCREngine()
        formatting_detector = FormattingDetector()
        
        # Step 1: Image preprocessing
        if preprocess:
            processed_image = preprocessor.preprocess(temp_path)
        else:
            processed_image = Image.open(temp_path)
        
        # Step 2: OCR
        ocr_data = ocr_engine.extract_text(processed_image, language)
        
        # Step 3: Formatting detection
        if detect_formatting:
            formatted_data = formatting_detector.detect_formatting(ocr_data, processed_image)
        else:
            formatted_data = ocr_data
        
        # Store in session state
        st.session_state.processed_data = formatted_data
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return formatted_data, None
        
    except Exception as e:
        return None, str(e)


def generate_word_document(formatted_data):
    """Generate Word document and return as bytes"""
    try:
        docx_generator = DOCXGenerator()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            output_path = tmp_file.name
        
        # Generate document
        docx_generator.create_document(formatted_data, output_path)
        
        # Read file as bytes
        with open(output_path, 'rb') as f:
            docx_bytes = f.read()
        
        # Clean up temporary file
        os.unlink(output_path)
        
        return docx_bytes, None
        
    except Exception as e:
        return None, str(e)


def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🖼️ Image to Word Converter</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6c757d;">Extract text from images while preserving formatting</p>', unsafe_allow_html=True)
    
    # Sidebar for options
    st.sidebar.header("⚙️ Processing Options")
    
    # Preprocessing option
    preprocess = st.sidebar.checkbox(
        "Apply Image Preprocessing",
        value=True,
        help="Improve OCR accuracy through noise reduction, deskewing, and contrast enhancement"
    )
    
    # Formatting detection option
    detect_formatting = st.sidebar.checkbox(
        "Detect Formatting (Bold/Italic)",
        value=True,
        help="Detect and preserve text formatting like bold, italic, and alignment"
    )
    
    # Language selection
    language_options = {
        "English": "eng",
        "English + German": "eng+deu",
        "English + French": "eng+fra"
    }
    selected_language = st.sidebar.selectbox(
        "Language",
        options=list(language_options.keys()),
        index=0,
        help="Select the language(s) for OCR recognition"
    )
    language_code = language_options[selected_language]
    
    # File upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.subheader("📁 Upload Image")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
        help="Supported formats: JPG, JPEG, PNG, BMP, TIFF"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    if uploaded_file is not None:
        # Display image preview
        st.markdown('<div class="preview-section">', unsafe_allow_html=True)
        st.subheader("📸 Image Preview")
        display_image_preview(uploaded_file)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Process button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Convert to Word", type="primary", use_container_width=True):
                with st.spinner("Processing image..."):
                    # Process the image
                    formatted_data, error = process_image(
                        uploaded_file, preprocess, detect_formatting, language_code
                    )
                    
                    if error:
                        st.markdown(f'<div class="error-message">❌ Error: {error}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="success-message">✅ Image processed successfully!</div>', unsafe_allow_html=True)
                        
                        # Display extracted text preview
                        st.markdown('<div class="preview-section">', unsafe_allow_html=True)
                        st.subheader("📝 Extracted Text Preview")
                        
                        # Get text preview
                        formatting_detector = FormattingDetector()
                        preview_text = formatting_detector.get_text_preview(formatted_data)
                        
                        st.text_area("Extracted Content", preview_text, height=200)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Generate download button
                        docx_bytes, error = generate_word_document(formatted_data)
                        
                        if error:
                            st.markdown(f'<div class="error-message">❌ Error generating document: {error}</div>', unsafe_allow_html=True)
                        else:
                            st.download_button(
                                label="📥 Download Word Document",
                                data=docx_bytes,
                                file_name="converted_document.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )
    
    else:
        # Instructions when no file is uploaded
        st.markdown("""
        <div class="preview-section">
            <h3>🚀 Getting Started</h3>
            <p>1. Upload an image using the file uploader above</p>
            <p>2. Adjust processing options in the sidebar if needed</p>
            <p>3. Click "Convert to Word" to extract text</p>
            <p>4. Download your formatted Word document</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown('<p style="text-align: center; color: #6c757d;">Built with ❤️ for FAST-NUCES BSAI Project Phase 1</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
