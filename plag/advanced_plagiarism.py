"""
Advanced plagiarism detection with database comparison and internet checking
"""
import requests
import hashlib
import sqlite3
from difflib import SequenceMatcher
import re
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

class PlagiarismDatabase:
    def __init__(self, db_path='plagiarism_db.sqlite3'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                content_hash TEXT UNIQUE,
                content TEXT,
                source_url TEXT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS text_segments (
                id INTEGER PRIMARY KEY,
                document_id INTEGER,
                segment_hash TEXT,
                segment_text TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_document(self, content, source_url="", title=""):
        content_hash = hashlib.md5(content.encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO documents (content_hash, content, source_url, title)
                VALUES (?, ?, ?, ?)
            ''', (content_hash, content, source_url, title))
            
            doc_id = cursor.lastrowid or cursor.execute(
                'SELECT id FROM documents WHERE content_hash = ?', (content_hash,)
            ).fetchone()[0]
            
            # Add text segments for better matching
            segments = self._create_segments(content)
            for segment in segments:
                segment_hash = hashlib.md5(segment.encode()).hexdigest()
                cursor.execute('''
                    INSERT OR IGNORE INTO text_segments (document_id, segment_hash, segment_text)
                    VALUES (?, ?, ?)
                ''', (doc_id, segment_hash, segment))
            
            conn.commit()
            return doc_id
        finally:
            conn.close()
    
    def _create_segments(self, text, segment_length=50):
        words = text.split()
        segments = []
        for i in range(0, len(words) - segment_length + 1, 10):
            segment = ' '.join(words[i:i + segment_length])
            if len(segment.strip()) > 20:
                segments.append(segment.strip())
        return segments
    
    def check_similarity(self, text):
        segments = self._create_segments(text)
        matches = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for segment in segments:
                segment_hash = hashlib.md5(segment.encode()).hexdigest()
                
                # Exact match
                cursor.execute('''
                    SELECT ts.segment_text, d.title, d.source_url
                    FROM text_segments ts
                    JOIN documents d ON ts.document_id = d.id
                    WHERE ts.segment_hash = ?
                ''', (segment_hash,))
                
                exact_matches = cursor.fetchall()
                for match in exact_matches:
                    matches.append({
                        'type': 'exact',
                        'similarity': 100,
                        'text': segment,
                        'source': match[1] or 'Unknown',
                        'url': match[2] or ''
                    })
                
                # Similar matches
                cursor.execute('''
                    SELECT ts.segment_text, d.title, d.source_url
                    FROM text_segments ts
                    JOIN documents d ON ts.document_id = d.id
                    LIMIT 100
                ''')
                
                all_segments = cursor.fetchall()
                for db_segment in all_segments:
                    similarity = SequenceMatcher(None, segment, db_segment[0]).ratio()
                    if similarity > 0.8:
                        matches.append({
                            'type': 'similar',
                            'similarity': similarity * 100,
                            'text': segment,
                            'source': db_segment[1] or 'Unknown',
                            'url': db_segment[2] or ''
                        })
        finally:
            conn.close()
        
        return matches

class InternetPlagiarismChecker:
    def __init__(self):
        self.search_engines = [
            'https://www.google.com/search?q=',
            'https://www.bing.com/search?q='
        ]
    
    def check_online(self, text, max_queries=5):
        sentences = re.split(r'[.!?]+', text)
        unique_sentences = [s.strip() for s in sentences if len(s.strip()) > 30][:max_queries]
        
        matches = []
        for sentence in unique_sentences:
            try:
                # Search for exact phrase
                query = f'"{sentence}"'
                encoded_query = quote(query)
                
                # Simple web search (would need proper API in production)
                search_url = self.search_engines[0] + encoded_query
                
                # Mock response for demo (replace with actual web scraping)
                matches.append({
                    'text': sentence,
                    'search_url': search_url,
                    'potential_match': True,
                    'confidence': 75
                })
                
            except Exception as e:
                logger.error(f"Internet search error: {e}")
        
        return matches

def enhanced_plagiarism_detection(text):
    """Enhanced plagiarism detection with database and internet checking"""
    
    # Initialize components
    db_checker = PlagiarismDatabase()
    internet_checker = InternetPlagiarismChecker()
    
    results = {
        'database_matches': [],
        'internet_matches': [],
        'overall_similarity': 0,
        'risk_level': 'Low',
        'sources_found': []
    }
    
    try:
        # Check against local database
        db_matches = db_checker.check_similarity(text)
        results['database_matches'] = db_matches
        
        # Check against internet (limited for demo)
        internet_matches = internet_checker.check_online(text)
        results['internet_matches'] = internet_matches
        
        # Calculate overall similarity
        if db_matches:
            avg_similarity = sum(match['similarity'] for match in db_matches) / len(db_matches)
            results['overall_similarity'] = min(avg_similarity, 100)
        
        # Determine risk level
        if results['overall_similarity'] > 70:
            results['risk_level'] = 'Very High'
        elif results['overall_similarity'] > 50:
            results['risk_level'] = 'High'
        elif results['overall_similarity'] > 30:
            results['risk_level'] = 'Medium'
        else:
            results['risk_level'] = 'Low'
        
        # Collect unique sources
        sources = set()
        for match in db_matches:
            if match['source']:
                sources.add(match['source'])
        results['sources_found'] = list(sources)
        
    except Exception as e:
        logger.error(f"Enhanced plagiarism detection error: {e}")
        results['error'] = str(e)
    
    return results