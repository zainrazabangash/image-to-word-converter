"""
OCR Engine Module
Integrates Tesseract OCR for text extraction from images.
"""

import pytesseract
from PIL import Image
import numpy as np


class OCREngine:
    """Handles OCR operations using Tesseract."""
    
    def __init__(self):
        # Configure Tesseract path for Windows
        # Common installation paths
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\%USERNAME%\AppData\Local\Tesseract-OCR\tesseract.exe',
        ]
        
        # Try to find Tesseract installation
        import os
        tesseract_found = False
        for path in possible_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                pytesseract.pytesseract.tesseract_cmd = expanded_path
                tesseract_found = True
                break
        
        if not tesseract_found:
            # Try to use tesseract from PATH
            try:
                pytesseract.get_tesseract_version()
                tesseract_found = True
            except Exception:
                print("Warning: Tesseract not found. Please install Tesseract OCR.")
    
    def extract_text(self, image, language='eng'):
        """
        Extract text from image using OCR.
        
        Args:
            image: PIL Image or numpy array
            language: Language code for OCR (default: 'eng')
            
        Returns:
            dict: OCR data containing text, confidence, and bounding boxes
        """
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Perform OCR with detailed output
        try:
            # Get text only
            text = pytesseract.image_to_string(image, lang=language)
            
            # Get detailed data including bounding boxes and confidence
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Get word-level bounding boxes
            words_data = self._extract_words_data(data)
            
            # Get line-level information
            lines_data = self._extract_lines_data(data)
            
            # Get paragraph information
            paragraphs_data = self._extract_paragraphs_data(data)
            
            result = {
                'text': text,
                'words': words_data,
                'lines': lines_data,
                'paragraphs': paragraphs_data,
                'raw_data': data,
                'language': language
            }
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"OCR failed: {str(e)}")
    
    def _extract_words_data(self, data):
        """Extract word-level information from OCR data."""
        words = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0:  # Valid word with confidence > 0
                word_info = {
                    'text': data['text'][i],
                    'confidence': int(data['conf'][i]),
                    'bbox': {
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    },
                    'line_num': data['line_num'][i],
                    'block_num': data['block_num'][i],
                    'par_num': data['par_num'][i]
                }
                words.append(word_info)
        
        return words
    
    def _extract_lines_data(self, data):
        """Extract line-level information from OCR data."""
        lines = {}
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0:
                line_key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
                
                if line_key not in lines:
                    lines[line_key] = {
                        'words': [],
                        'bbox': {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        },
                        'confidence': int(data['conf'][i])
                    }
                else:
                    # Update bounding box to encompass all words
                    line = lines[line_key]
                    line['words'].append(data['text'][i])
                    line['bbox']['width'] = max(
                        line['bbox']['width'],
                        data['left'][i] + data['width'][i] - line['bbox']['x']
                    )
                    line['bbox']['height'] = max(
                        line['bbox']['height'],
                        data['top'][i] + data['height'][i] - line['bbox']['y']
                    )
                    line['confidence'] = min(line['confidence'], int(data['conf'][i]))
        
        # Convert words lists to text
        for line_key in lines:
            lines[line_key]['text'] = ' '.join(lines[line_key]['words'])
            del lines[line_key]['words']
        
        return list(lines.values())
    
    def _extract_paragraphs_data(self, data):
        """Extract paragraph-level information from OCR data."""
        paragraphs = {}
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0:
                par_key = (data['block_num'][i], data['par_num'][i])
                
                if par_key not in paragraphs:
                    paragraphs[par_key] = {
                        'lines': [],
                        'bbox': {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        }
                    }
                else:
                    par = paragraphs[par_key]
                    par['bbox']['width'] = max(
                        par['bbox']['width'],
                        data['left'][i] + data['width'][i] - par['bbox']['x']
                    )
                    par['bbox']['height'] = max(
                        par['bbox']['height'],
                        data['top'][i] + data['height'][i] - par['bbox']['y']
                    )
        
        return list(paragraphs.values())
    
    def get_available_languages(self):
        """Get list of available Tesseract languages."""
        try:
            languages = pytesseract.get_languages()
            return languages
        except Exception:
            return ['eng']  # Default to English if cannot get list
