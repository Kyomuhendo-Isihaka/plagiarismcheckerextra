#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spc.settings')
django.setup()

from plag.plagiarismeng import extract_document_text
from pathlib import Path

def test_document_extraction():
    print("Testing Document Extraction...")
    
    # Create test directory
    test_dir = Path("test_documents")
    test_dir.mkdir(exist_ok=True)
    
    # Create a test text file
    test_txt = test_dir / "test.txt"
    with open(test_txt, 'w', encoding='utf-8') as f:
        f.write("This is a test document with some sample text content for testing the extraction functionality.")
    
    # Test text extraction
    try:
        text = extract_document_text(str(test_txt))
        print(f"TXT Extraction: {'SUCCESS' if text and len(text) > 0 else 'FAILED'}")
        if text:
            print(f"Extracted text: {text[:100]}...")
    except Exception as e:
        print(f"TXT Extraction FAILED: {e}")
    
    # Test with non-existent file
    try:
        text = extract_document_text("nonexistent.pdf")
        print(f"Non-existent file handling: {'SUCCESS' if 'not found' in text.lower() else 'FAILED'}")
    except Exception as e:
        print(f"Non-existent file test: {e}")
    
    # Clean up
    if test_txt.exists():
        test_txt.unlink()
    if test_dir.exists():
        test_dir.rmdir()
    
    print("Document extraction test completed!")

if __name__ == "__main__":
    test_document_extraction()