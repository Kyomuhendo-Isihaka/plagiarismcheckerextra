from difflib import SequenceMatcher
from django.conf import settings 
from django.http import JsonResponse
import os 
import threading
import uuid
import fitz
import logging
from pathlib import Path
import docx
import zipfile
import xml.etree.ElementTree as ET
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    HTML_PARSER_AVAILABLE = True
except ImportError:
    HTML_PARSER_AVAILABLE = False

try:
    import ebooklib
    from ebooklib import epub
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False
from .security import (
    validate_file_upload, generate_secure_filename, 
    validate_file_path, check_file_content_type
)
from .ai_detector import ai_detector

# Optional enhanced features
try:
    from .ml_ai_detector import ml_ai_detector
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

try:
    from .advanced_plagiarism import enhanced_plagiarism_detection
    ENHANCED_PLAG_AVAILABLE = True
except ImportError:
    ENHANCED_PLAG_AVAILABLE = False

try:
    from .ocr_engine import ocr_engine
    ENHANCED_OCR_AVAILABLE = True
except ImportError:
    ENHANCED_OCR_AVAILABLE = False

try:
    from .grammar_checker import grammar_checker
    GRAMMAR_CHECKER_AVAILABLE = True
except ImportError:
    GRAMMAR_CHECKER_AVAILABLE = False

logger = logging.getLogger(__name__)
speaker = None

def init_speaker():
    # Disabled to prevent blocking
    return None

def speak(words):
    # Disabled to prevent blocking - use client-side TTS instead
    logger.info(f"TTS requested for {len(words)} characters (disabled)")
    return

def extract_document_text(file_path):
    """Extract text from various document formats"""
    try:
        # Use security validation for file path
        media_dir = Path(settings.MEDIA_ROOT)
        if not file_path.startswith(str(media_dir)):
            file_path = media_dir / file_path
        else:
            file_path = Path(file_path)
        
        # Validate file path using security utility
        validated_path = validate_file_path(str(file_path), str(media_dir))
        file_path = Path(validated_path)
            
        if not file_path.exists() or not file_path.is_file():
            return "Document not found"
            
        # Check file size (limit to 50MB)
        if file_path.stat().st_size > 50 * 1024 * 1024:
            logger.warning(f"Large file access attempt: {file_path}")
            return "File too large"

        # Get file extension
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.pdf':
            return extract_pdf_content(file_path)
        elif file_ext in ['.docx', '.doc']:
            return extract_docx_content(file_path)
        elif file_ext == '.txt':
            return extract_txt_content(file_path)
        elif file_ext == '.html':
            return extract_html_content(file_path)
        elif file_ext == '.epub':
            return extract_epub_content(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            return extract_image_text(file_path)
        else:
            return "Unsupported file format"
        
    except Exception as e:
        logger.error(f"Document extraction error: {e}")
        return "Error extracting document text"

def extract_pdf_content(file_path):
    """Extract text from PDF files"""
    try:
        doc = fitz.open(str(file_path))
        text = ""
        max_pages = 100
        max_chars = 50000
        
        for i, page in enumerate(doc):
            if i >= max_pages or len(text) >= max_chars:
                break
            page_text = page.get_text()
            if len(text) + len(page_text) > max_chars:
                text += page_text[:max_chars - len(text)]
                break
            text += page_text
            
        doc.close()
        return text.strip() or "No text content found in PDF"
        
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return "Error reading PDF file"

def extract_docx_content(file_path):
    """Extract text from DOCX files"""
    try:
        doc = docx.Document(str(file_path))
        text = ""
        max_chars = 50000
        
        for paragraph in doc.paragraphs:
            if len(text) >= max_chars:
                break
            para_text = paragraph.text
            if len(text) + len(para_text) > max_chars:
                text += para_text[:max_chars - len(text)]
                break
            text += para_text + "\n"
            
        return text.strip() or "No text content found in document"
        
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return "Error reading DOCX file"

def extract_txt_content(file_path):
    """Extract text from TXT files"""
    try:
        max_chars = 50000
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            text = file.read(max_chars)
        return text.strip() or "No text content found in file"
        
    except Exception as e:
        logger.error(f"TXT extraction error: {e}")
        return "Error reading text file"

def extract_html_content(file_path):
    """Extract text from HTML files"""
    try:
        if not HTML_PARSER_AVAILABLE:
            # Fallback to basic HTML parsing
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                # Basic HTML tag removal
                import re
                text = re.sub(r'<[^>]+>', '', content)
                text = re.sub(r'\s+', ' ', text)
                return text[:50000] or "No text content found in HTML"
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text[:50000] or "No text content found in HTML"
    except Exception as e:
        logger.error(f"HTML extraction error: {e}")
        return "Error reading HTML file"

def extract_epub_content(file_path):
    """Extract text from EPUB files"""
    try:
        if not EPUB_AVAILABLE:
            return "EPUB support not available - missing ebooklib dependency"
        
        book = epub.read_epub(str(file_path))
        text = ""
        max_chars = 50000
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                if HTML_PARSER_AVAILABLE:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    chapter_text = soup.get_text()
                else:
                    # Basic HTML tag removal
                    import re
                    content = item.get_content().decode('utf-8', errors='ignore')
                    chapter_text = re.sub(r'<[^>]+>', '', content)
                    chapter_text = re.sub(r'\s+', ' ', chapter_text)
                
                if len(text) + len(chapter_text) > max_chars:
                    text += chapter_text[:max_chars - len(text)]
                    break
                text += chapter_text + "\n\n"
                
        return text.strip() or "No text content found in EPUB"
    except Exception as e:
        logger.error(f"EPUB extraction error: {e}")
        return "Error reading EPUB file"

def extract_image_text(file_path):
    """Extract text from images using OCR"""
    try:
        if ENHANCED_OCR_AVAILABLE:
            # Use enhanced OCR engine with multiple backends
            text = ocr_engine.extract_text(file_path)
            return text or "No text found in image"
        elif OCR_AVAILABLE:
            # Fallback to basic OCR
            image = Image.open(str(file_path))
            text = pytesseract.image_to_string(image)
            return text.strip() or "No text found in image"
        else:
            return "OCR not available - install pytesseract for image text extraction"
    except Exception as e:
        logger.error(f"Image extraction error: {e}")
        return "Error reading image file"

# Keep old function for backward compatibility
def extract_pdf_text(pdf_file):
    return extract_document_text(pdf_file)

def upload_file(request):
    try:
        if request.method != 'POST' or 'u_file' not in request.FILES:
            return None
            
        uploaded_file = request.FILES['u_file']
        
        # Use security validation
        validate_file_upload(uploaded_file)
        
        # Generate secure filename
        filename = generate_secure_filename(uploaded_file.name)
        
        # Support additional file types
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.html', '.epub', '.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        file_ext = Path(filename).suffix.lower()
        if file_ext not in allowed_extensions:
            logger.warning(f"Unsupported file type: {file_ext}")
            return None
        
        # Ensure media directory exists
        media_dir = Path(settings.MEDIA_ROOT)
        media_dir.mkdir(exist_ok=True, mode=0o755)
        
        file_path = media_dir / filename
        
        # Write file securely with restricted permissions
        with open(file_path, 'wb') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Set secure file permissions
        os.chmod(file_path, 0o644)
        
        # Validate file content matches extension
        if not check_file_content_type(str(file_path)):
            os.remove(file_path)
            logger.warning(f"File content validation failed: {uploaded_file.name}")
            return None
                
        return str(file_path)
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        return None

def analyze_document(text):
    """Enhanced document analysis with ML and database checking"""
    try:
        if not text or len(text.strip()) < 50:
            return {
                'plagiarism': {'similarity': 0, 'sources': []},
                'ai_detection': {'is_ai_generated': False, 'confidence': 0, 'indicators': [], 'risk_level': 'Very Low'},
                'word_count': 0,
                'character_count': 0,
                'error': 'Text too short for analysis'
            }
        
        # AI Detection (with ML if available)
        if ML_AVAILABLE:
            try:
                ml_ai_results = ml_ai_detector.predict_ai_content(text)
                rule_based_results = ai_detector.detect_ai_content(text)
                
                # Merge AI detection results
                ai_results = {
                    'is_ai_generated': ml_ai_results['is_ai_generated'] or rule_based_results['is_ai_generated'],
                    'confidence': max(ml_ai_results['confidence'], rule_based_results['confidence']),
                    'ml_score': ml_ai_results.get('ml_score', 0),
                    'feature_analysis': ml_ai_results.get('feature_analysis', {}),
                    'indicators': list(set(ml_ai_results['indicators'] + rule_based_results['indicators'])),
                    'risk_level': ml_ai_results['risk_level']
                }
            except Exception as e:
                logger.error(f"ML AI detection failed: {e}")
                ai_results = ai_detector.detect_ai_content(text)
        else:
            # Fallback to basic AI detection
            ai_results = ai_detector.detect_ai_content(text)
        
        # Plagiarism detection (enhanced if available)
        if ENHANCED_PLAG_AVAILABLE:
            try:
                enhanced_plag_results = enhanced_plagiarism_detection(text)
                plagiarism_results = {
                    'similarity': enhanced_plag_results['overall_similarity'],
                    'sources': enhanced_plag_results['sources_found'],
                    'database_matches': enhanced_plag_results.get('database_matches', []),
                    'internet_matches': enhanced_plag_results.get('internet_matches', []),
                    'risk_level': enhanced_plag_results['risk_level']
                }
            except Exception as e:
                logger.error(f"Enhanced plagiarism detection failed: {e}")
                plagiarism_results = detect_plagiarism(text)
        else:
            # Fallback to basic detection
            plagiarism_results = detect_plagiarism(text)
        
        # Document statistics
        words = text.split()
        word_count = len(words)
        character_count = len(text)
        
        # Reading time (average 200 words per minute)
        reading_time = max(1, word_count // 200)
        
        # Grammar and readability analysis
        grammar_results = {}
        if GRAMMAR_CHECKER_AVAILABLE:
            try:
                grammar_issues = grammar_checker.check_grammar(text)
                readability = grammar_checker.analyze_readability(text)
                writing_style = grammar_checker.analyze_writing_style(text)
                
                grammar_results = {
                    'grammar_issues': grammar_issues,
                    'readability': readability,
                    'writing_style': writing_style
                }
            except Exception as e:
                logger.error(f"Grammar analysis failed: {e}")
        
        results = {
            'plagiarism': plagiarism_results,
            'ai_detection': ai_results,
            'grammar_analysis': grammar_results,
            'word_count': word_count,
            'character_count': character_count,
            'reading_time': reading_time,
            'sentences': len([s for s in text.split('.') if s.strip()]),
            'paragraphs': len([p for p in text.split('\n\n') if p.strip()]),
            'enhanced_features': ML_AVAILABLE and ENHANCED_PLAG_AVAILABLE and GRAMMAR_CHECKER_AVAILABLE
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Document analysis error: {e}")
        return {
            'plagiarism': {'similarity': 0, 'sources': []},
            'ai_detection': {'is_ai_generated': False, 'confidence': 0, 'indicators': [], 'risk_level': 'Very Low'},
            'word_count': 0,
            'character_count': 0,
            'error': str(e)
        }

def detect_plagiarism(text):
    """Enhanced plagiarism detection with pattern analysis"""
    try:
        # Common academic phrases that might indicate copying
        common_phrases = [
            "according to the research", "studies have shown", "it has been found",
            "research indicates", "the literature suggests", "previous studies",
            "in conclusion", "to summarize", "furthermore", "moreover",
            "however", "nevertheless", "on the other hand"
        ]
        
        # Check for excessive use of common academic phrases
        phrase_count = 0
        text_lower = text.lower()
        for phrase in common_phrases:
            phrase_count += text_lower.count(phrase)
        
        words = text.split()
        if len(words) == 0:
            return {'similarity': 0, 'sources': [], 'indicators': []}
        
        # Calculate similarity score based on phrase density
        phrase_density = (phrase_count / len(words)) * 100
        
        # Check for repetitive patterns
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        repetitive_score = 0
        
        if len(sentences) > 3:
            # Check for similar sentence structures
            similar_starts = 0
            for i in range(len(sentences) - 1):
                if len(sentences[i].split()) > 2 and len(sentences[i+1].split()) > 2:
                    start1 = ' '.join(sentences[i].split()[:3]).lower()
                    start2 = ' '.join(sentences[i+1].split()[:3]).lower()
                    if SequenceMatcher(None, start1, start2).ratio() > 0.7:
                        similar_starts += 1
            
            repetitive_score = (similar_starts / len(sentences)) * 100
        
        # Combine scores for overall similarity
        similarity_score = min(100, phrase_density * 2 + repetitive_score)
        
        indicators = []
        if phrase_density > 5:
            indicators.append(f"High density of academic phrases ({phrase_density:.1f}%)")
        if repetitive_score > 20:
            indicators.append(f"Repetitive sentence structures ({repetitive_score:.1f}%)")
        
        return {
            'similarity': round(similarity_score, 1),
            'sources': [],  # Would connect to external plagiarism databases in production
            'indicators': indicators,
            'phrase_density': round(phrase_density, 2),
            'repetitive_score': round(repetitive_score, 2)
        }
        
    except Exception as e:
        logger.error(f"Plagiarism detection error: {e}")
        return {'similarity': 0, 'sources': [], 'indicators': []}

def read_pdf(file_path):
    """Read document content - supports multiple formats"""
    try:
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return None
        
        text = extract_document_text(file_path)
        return text if text and not text.startswith("Error") and not text.startswith("Document not found") else None
            
    except Exception as e:
        logger.error(f"Document reading error: {e}")
        return None