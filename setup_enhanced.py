#!/usr/bin/env python
"""
Setup script for enhanced plagiarism checker features
"""
import os
import sys
import subprocess
import sqlite3

def install_requirements():
    """Install enhanced requirements"""
    print("Installing enhanced requirements...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_enhanced.txt'])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def setup_plagiarism_database():
    """Initialize plagiarism database with sample data"""
    print("Setting up plagiarism database...")
    
    from plag.advanced_plagiarism import PlagiarismDatabase
    
    db = PlagiarismDatabase()
    
    # Add some sample documents for testing
    sample_docs = [
        {
            'content': "The quick brown fox jumps over the lazy dog. This is a common pangram used in typography.",
            'title': "Sample Pangram",
            'source_url': "https://example.com/pangram"
        },
        {
            'content': "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.",
            'title': "ML Definition",
            'source_url': "https://example.com/ml"
        },
        {
            'content': "Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.",
            'title': "Django Description",
            'source_url': "https://djangoproject.com"
        }
    ]
    
    for doc in sample_docs:
        try:
            db.add_document(doc['content'], doc['source_url'], doc['title'])
            print(f"✅ Added sample document: {doc['title']}")
        except Exception as e:
            print(f"❌ Failed to add document: {e}")
    
    print("✅ Plagiarism database initialized")

def check_ocr_engines():
    """Check which OCR engines are available"""
    print("Checking OCR engines...")
    
    from plag.ocr_engine import ocr_engine
    
    info = ocr_engine.get_engine_info()
    
    print(f"Available OCR engines: {info['available_engines']}")
    print(f"Total engines: {info['total_engines']}")
    
    if info['recommended_install']:
        print("Recommended installations:")
        for install_cmd in info['recommended_install']:
            print(f"  {install_cmd}")
    
    return info['total_engines'] > 0

def test_enhanced_features():
    """Test enhanced features"""
    print("Testing enhanced features...")
    
    # Test ML AI detector
    try:
        from plag.ml_ai_detector import ml_ai_detector
        
        test_text = "Furthermore, it is important to note that machine learning algorithms can be used to detect patterns in data. Moreover, these algorithms are particularly effective when dealing with large datasets."
        
        result = ml_ai_detector.predict_ai_content(test_text)
        print(f"✅ ML AI Detection: {result['confidence']:.1f}% confidence")
        
    except Exception as e:
        print(f"❌ ML AI Detection failed: {e}")
    
    # Test enhanced plagiarism
    try:
        from plag.advanced_plagiarism import enhanced_plagiarism_detection
        
        test_text = "The quick brown fox jumps over the lazy dog."
        result = enhanced_plagiarism_detection(test_text)
        print(f"✅ Enhanced Plagiarism: {result['overall_similarity']:.1f}% similarity")
        
    except Exception as e:
        print(f"❌ Enhanced Plagiarism failed: {e}")
    
    # Test OCR
    ocr_available = check_ocr_engines()
    if ocr_available:
        print("✅ OCR engines available")
    else:
        print("⚠️ No OCR engines available - install pytesseract, easyocr, or paddleocr")

def main():
    """Main setup function"""
    print("🚀 Setting up Enhanced Plagiarism Checker")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Please run this script from the Django project root directory")
        return
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed - could not install requirements")
        return
    
    # Setup Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spc.settings')
    
    try:
        import django
        django.setup()
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return
    
    # Initialize plagiarism database
    try:
        setup_plagiarism_database()
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
    
    # Test features
    test_enhanced_features()
    
    print("\n🎉 Enhanced Plagiarism Checker setup complete!")
    print("\nNew Features Available:")
    print("✅ ML-powered AI detection with feature analysis")
    print("✅ Database-based plagiarism comparison")
    print("✅ Internet plagiarism checking (basic)")
    print("✅ Enhanced OCR with multiple engines")
    print("\nTo use enhanced features, restart your Django server.")

if __name__ == '__main__':
    main()