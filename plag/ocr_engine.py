"""
Enhanced OCR engine with multiple backends
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self):
        self.available_engines = []
        self._check_available_engines()
    
    def _check_available_engines(self):
        """Check which OCR engines are available"""
        
        # Try Tesseract
        try:
            import pytesseract
            from PIL import Image
            self.available_engines.append('tesseract')
            logger.info("Tesseract OCR available")
        except ImportError:
            logger.info("Tesseract OCR not available")
        
        # Try EasyOCR
        try:
            import easyocr
            self.available_engines.append('easyocr')
            logger.info("EasyOCR available")
        except ImportError:
            logger.info("EasyOCR not available")
        
        # Try PaddleOCR
        try:
            import paddleocr
            self.available_engines.append('paddleocr')
            logger.info("PaddleOCR available")
        except ImportError:
            logger.info("PaddleOCR not available")
    
    def extract_text_tesseract(self, image_path):
        """Extract text using Tesseract OCR"""
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(image_path)
            
            # Preprocess image for better OCR
            image = image.convert('RGB')
            
            # Extract text with configuration
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?;: '
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Tesseract OCR error: {e}")
            return None
    
    def extract_text_easyocr(self, image_path):
        """Extract text using EasyOCR"""
        try:
            import easyocr
            
            reader = easyocr.Reader(['en'])
            results = reader.readtext(str(image_path))
            
            # Combine all detected text
            text_parts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Only include high-confidence text
                    text_parts.append(text)
            
            return ' '.join(text_parts)
            
        except Exception as e:
            logger.error(f"EasyOCR error: {e}")
            return None
    
    def extract_text_paddleocr(self, image_path):
        """Extract text using PaddleOCR"""
        try:
            import paddleocr
            
            ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            results = ocr.ocr(str(image_path), cls=True)
            
            # Extract text from results
            text_parts = []
            for line in results:
                for word_info in line:
                    text = word_info[1][0]
                    confidence = word_info[1][1]
                    if confidence > 0.5:
                        text_parts.append(text)
            
            return ' '.join(text_parts)
            
        except Exception as e:
            logger.error(f"PaddleOCR error: {e}")
            return None
    
    def extract_text(self, image_path):
        """Extract text using the best available OCR engine"""
        
        if not self.available_engines:
            return "No OCR engines available. Install pytesseract, easyocr, or paddleocr."
        
        results = {}
        
        # Try each available engine
        for engine in self.available_engines:
            try:
                if engine == 'tesseract':
                    text = self.extract_text_tesseract(image_path)
                elif engine == 'easyocr':
                    text = self.extract_text_easyocr(image_path)
                elif engine == 'paddleocr':
                    text = self.extract_text_paddleocr(image_path)
                else:
                    continue
                
                if text and len(text.strip()) > 0:
                    results[engine] = text
                    
            except Exception as e:
                logger.error(f"OCR engine {engine} failed: {e}")
                continue
        
        if not results:
            return "No text could be extracted from the image."
        
        # Return the longest result (usually most accurate)
        best_result = max(results.values(), key=len)
        return best_result
    
    def get_engine_info(self):
        """Get information about available OCR engines"""
        info = {
            'available_engines': self.available_engines,
            'total_engines': len(self.available_engines),
            'recommended_install': []
        }
        
        if 'tesseract' not in self.available_engines:
            info['recommended_install'].append('pip install pytesseract pillow')
        
        if 'easyocr' not in self.available_engines:
            info['recommended_install'].append('pip install easyocr')
        
        if 'paddleocr' not in self.available_engines:
            info['recommended_install'].append('pip install paddleocr')
        
        return info

# Global OCR engine instance
ocr_engine = OCREngine()