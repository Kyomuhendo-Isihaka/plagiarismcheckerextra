"""
Security utilities for the plagiarism checker application
"""
import os
import hashlib
import secrets
from pathlib import Path
from django.conf import settings
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

def validate_file_upload(uploaded_file):
    """
    Validate uploaded file for security
    """
    if not uploaded_file:
        raise ValidationError("No file provided")
    
    # Check file size (50MB limit)
    max_size = 50 * 1024 * 1024
    if uploaded_file.size > max_size:
        raise ValidationError(f"File too large. Maximum size is {max_size // (1024*1024)}MB")
    
    # Check file extension
    allowed_extensions = ['.pdf', '.txt', '.doc', '.docx']
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in allowed_extensions:
        raise ValidationError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
    
    # Check filename for malicious patterns
    if any(char in uploaded_file.name for char in ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']):
        raise ValidationError("Invalid characters in filename")
    
    return True

def generate_secure_filename(original_filename):
    """
    Generate a secure filename using UUID and preserve extension
    """
    file_ext = os.path.splitext(original_filename)[1].lower()
    secure_name = secrets.token_urlsafe(32) + file_ext
    return secure_name

def validate_file_path(file_path, base_directory=None):
    """
    Validate file path to prevent directory traversal attacks
    """
    if not base_directory:
        base_directory = settings.MEDIA_ROOT
    
    try:
        # Resolve paths to absolute paths
        file_path = Path(file_path).resolve()
        base_directory = Path(base_directory).resolve()
        
        # Check if file path is within base directory
        if not str(file_path).startswith(str(base_directory)):
            logger.warning(f"Path traversal attempt: {file_path}")
            raise ValidationError("Invalid file path")
        
        return str(file_path)
    except Exception as e:
        logger.error(f"Path validation error: {e}")
        raise ValidationError("Invalid file path")

def sanitize_input(text, max_length=None):
    """
    Sanitize user input
    """
    if not text:
        return ""
    
    # Remove null bytes and control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
    
    # Strip whitespace
    text = text.strip()
    
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

def check_file_content_type(file_path):
    """
    Check if file content matches its extension
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(1024)
        
        file_lower = file_path.lower()
        
        # PDF signature
        if file_lower.endswith('.pdf'):
            return header.startswith(b'%PDF-')
        
        # DOCX signature (ZIP format)
        if file_lower.endswith('.docx'):
            return header.startswith(b'PK\x03\x04') or header.startswith(b'PK\x05\x06') or header.startswith(b'PK\x07\x08')
        
        # DOC signature
        if file_lower.endswith('.doc'):
            return header.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1') or header.startswith(b'\x0d\x44\x4f\x43')
        
        # Basic text file check
        if file_lower.endswith('.txt'):
            try:
                header.decode('utf-8')
                return True
            except UnicodeDecodeError:
                # Try other common encodings
                try:
                    header.decode('latin-1')
                    return True
                except:
                    return False
        
        return True  # Allow other types for now
    except Exception as e:
        logger.error(f"Content type check error: {e}")
        return False

def log_security_event(event_type, user_id, details):
    """
    Log security events
    """
    logger.warning(f"SECURITY EVENT - Type: {event_type}, User: {user_id}, Details: {details}")

class RateLimiter:
    """
    Simple in-memory rate limiter
    """
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, identifier, max_requests=10, window_seconds=60):
        """
        Rate limiting disabled - always allow requests
        """
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()