"""
Image Preprocessing Module
Handles image enhancement and preprocessing for better OCR results.
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance


class ImagePreprocessor:
    """Preprocesses images to improve OCR accuracy."""
    
    def __init__(self):
        self.target_dpi = 300
    
    def preprocess(self, image_path):
        """
        Apply preprocessing steps to improve OCR quality.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            PIL.Image: Preprocessed image
        """
        # Load image
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Noise reduction
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Adaptive thresholding for better contrast
        binary = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        
        # Deskew if needed
        deskewed = self._deskew(binary)
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(deskewed)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(processed_image)
        processed_image = enhancer.enhance(1.5)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(processed_image)
        processed_image = enhancer.enhance(1.2)
        
        return processed_image
    
    def _deskew(self, image):
        """
        Deskew the image if it has significant rotation.
        
        Args:
            image: Grayscale numpy array
            
        Returns:
            numpy array: Deskewed image
        """
        # Find all non-zero points
        coords = np.column_stack(np.where(image > 0))
        
        if len(coords) < 100:
            return image
        
        # Calculate angle
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Only deskew if angle is significant (> 0.5 degrees)
        if abs(angle) < 0.5:
            return image
        
        # Rotate the image
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        return rotated
    
    def get_image_stats(self, image):
        """
        Get image statistics useful for OCR.
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            dict: Image statistics
        """
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        stats = {
            'mean': np.mean(gray),
            'std': np.std(gray),
            'dimensions': image.shape[:2],
            'is_dark': np.mean(gray) < 127
        }
        
        return stats
