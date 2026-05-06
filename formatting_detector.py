"""
Formatting Detection Module
Detects text formatting attributes like bold, italic, alignment, and paragraphs.
"""

import cv2
import numpy as np
from PIL import Image


class FormattingDetector:
    """Detects formatting attributes from OCR data and image analysis."""
    
    def __init__(self):
        self.bold_threshold = 1.3  # Thickness ratio threshold for bold text
        self.italic_slant_threshold = 0.15  # Slant ratio threshold for italic
    
    def detect_formatting(self, ocr_data, image):
        """
        Detect formatting attributes from OCR data and image.
        
        Args:
            ocr_data: Dictionary containing OCR results
            image: PIL Image or numpy array
            
        Returns:
            dict: Enhanced OCR data with formatting information
        """
        if isinstance(image, Image.Image):
            image_array = np.array(image)
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array
        else:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
        
        # Add formatting info to each word
        formatted_words = []
        for word in ocr_data['words']:
            bbox = word['bbox']
            word_img = gray[bbox['y']:bbox['y']+bbox['height'], 
                           bbox['x']:bbox['x']+bbox['width']]
            
            if word_img.size > 0:
                formatting = self._analyze_word_formatting(word_img, word)
                word_with_formatting = {**word, **formatting}
                formatted_words.append(word_with_formatting)
            else:
                formatted_words.append({**word, 'is_bold': False, 'is_italic': False})
        
        # Detect alignment for each paragraph
        paragraphs_with_alignment = self._detect_paragraph_alignment(
            ocr_data['paragraphs'], 
            ocr_data['lines'],
            gray.shape[1]  # Image width
        )
        
        # Compile enhanced data
        result = {
            **ocr_data,
            'words': formatted_words,
            'paragraphs': paragraphs_with_alignment,
            'image_width': gray.shape[1],
            'image_height': gray.shape[0]
        }
        
        return result
    
    def _analyze_word_formatting(self, word_img, word_info):
        """
        Analyze a single word image for formatting attributes.
        
        Args:
            word_img: Grayscale image of the word
            word_info: Dictionary with word information
            
        Returns:
            dict: Formatting attributes
        """
        formatting = {
            'is_bold': False,
            'is_italic': False,
            'font_size': self._estimate_font_size(word_info),
            'text_color': 'black'  # Default assumption
        }
        
        # Detect bold by analyzing stroke thickness
        formatting['is_bold'] = self._detect_bold(word_img, word_info)
        
        # Detect italic by analyzing slant
        formatting['is_italic'] = self._detect_italic(word_img)
        
        return formatting
    
    def _detect_bold(self, word_img, word_info):
        """
        Detect if text is bold based on stroke thickness and intensity.
        
        Args:
            word_img: Grayscale image of word
            word_info: Dictionary with word information
            
        Returns:
            bool: True if text appears bold
        """
        if word_img.size == 0:
            return False
        
        # Binarize the image
        _, binary = cv2.threshold(word_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Calculate average stroke thickness using erosion
        kernel = np.ones((3, 3), np.uint8)
        eroded = cv2.erode(binary, kernel, iterations=1)
        
        original_pixels = np.sum(binary > 0)
        eroded_pixels = np.sum(eroded > 0)
        
        if original_pixels == 0:
            return False
        
        # Calculate thickness ratio
        thickness_ratio = original_pixels / (eroded_pixels + 1)
        
        # Bold text typically has higher thickness ratio
        # and higher average intensity (darker text)
        mean_intensity = np.mean(word_img)
        
        is_bold = (thickness_ratio > self.bold_threshold and 
                   mean_intensity < 100)  # Dark text
        
        return is_bold
    
    def _detect_italic(self, word_img):
        """
        Detect if text is italic based on slant analysis.
        
        Args:
            word_img: Grayscale image of word
            
        Returns:
            bool: True if text appears italic
        """
        if word_img.size == 0:
            return False
        
        # Binarize
        _, binary = cv2.threshold(word_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return False
        
        # Analyze slant of character components
        slant_angles = []
        
        for contour in contours:
            if len(contour) < 5:
                continue
            
            # Fit rotated rectangle
            rect = cv2.minAreaRect(contour)
            angle = rect[2]
            
            # Normalize angle
            if angle < -45:
                angle = 90 + angle
            
            # Filter out extreme angles
            if abs(angle) < 60 and abs(angle) > 5:
                slant_angles.append(abs(angle))
        
        # If majority of characters have consistent slant, likely italic
        if slant_angles:
            avg_slant = np.mean(slant_angles)
            is_italic = avg_slant > 8  # Threshold angle in degrees
            return is_italic
        
        return False
    
    def _estimate_font_size(self, word_info):
        """
        Estimate font size based on word height.
        
        Args:
            word_info: Dictionary with word information
            
        Returns:
            int: Estimated font size in points
        """
        # Approximate conversion: pixel height to font points
        # Standard DPI assumption: 96 pixels per inch
        height_pixels = word_info['bbox']['height']
        estimated_size = int(height_pixels * 0.75)  # Rough approximation
        
        # Clamp to reasonable font sizes
        return max(8, min(72, estimated_size))
    
    def _detect_paragraph_alignment(self, paragraphs, lines, image_width):
        """
        Detect text alignment (left, center, right, justify) for each paragraph.
        
        Args:
            paragraphs: List of paragraph data
            lines: List of line data
            image_width: Width of the image in pixels
            
        Returns:
            list: Paragraphs with alignment information
        """
        margin_threshold = 0.15  # 15% of image width
        
        for paragraph in paragraphs:
            par_bbox = paragraph['bbox']
            
            # Find lines belonging to this paragraph
            par_lines = [line for line in lines 
                        if self._line_in_paragraph(line, par_bbox)]
            
            if not par_lines:
                paragraph['alignment'] = 'left'
                continue
            
            # Analyze margins
            left_margins = []
            right_margins = []
            
            for line in par_lines:
                line_bbox = line['bbox']
                left_margin = line_bbox['x']
                right_margin = image_width - (line_bbox['x'] + line_bbox['width'])
                
                left_margins.append(left_margin)
                right_margins.append(right_margin)
            
            avg_left_margin = np.mean(left_margins)
            avg_right_margin = np.mean(right_margins)
            
            # Determine alignment
            left_margin_ratio = avg_left_margin / image_width
            right_margin_ratio = avg_right_margin / image_width
            
            # Check for center alignment (both margins roughly equal)
            margin_diff = abs(left_margin_ratio - right_margin_ratio)
            
            if margin_diff < 0.05:  # Margins are similar
                if left_margin_ratio > 0.1:  # Significant margins on both sides
                    paragraph['alignment'] = 'center'
                else:
                    paragraph['alignment'] = 'justify'
            elif right_margin_ratio < left_margin_ratio * 0.3:
                paragraph['alignment'] = 'right'
            else:
                paragraph['alignment'] = 'left'
        
        return paragraphs
    
    def _line_in_paragraph(self, line, par_bbox):
        """Check if a line belongs to a paragraph based on overlapping y-coordinates."""
        line_y = line['bbox']['y']
        line_bottom = line['bbox']['y'] + line['bbox']['height']
        par_y = par_bbox['y']
        par_bottom = par_bbox['y'] + par_bbox['height']
        
        # Check for vertical overlap
        return (line_y < par_bottom and line_bottom > par_y)
    
    def get_text_preview(self, formatted_data):
        """
        Generate a text preview with formatting indicators.
        
        Args:
            formatted_data: Enhanced OCR data with formatting
            
        Returns:
            str: Text preview with formatting markers
        """
        lines = []
        current_line = 1
        line_text = ""
        
        for word in formatted_data['words']:
            # Check if new line
            if word['line_num'] != current_line:
                if line_text:
                    lines.append(line_text)
                line_text = ""
                current_line = word['line_num']
            
            # Add formatting markers
            prefix = ""
            suffix = ""
            
            if word.get('is_bold'):
                prefix += "**"
                suffix = "**" + suffix
            
            if word.get('is_italic'):
                prefix += "*"
                suffix = "*" + suffix
            
            line_text += prefix + word['text'] + suffix + " "
        
        # Add last line
        if line_text:
            lines.append(line_text)
        
        return "\n".join(lines)
