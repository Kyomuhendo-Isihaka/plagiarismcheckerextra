import requests
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from urllib.parse import quote

class RealPlagiarismDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    def detect_plagiarism(self, text):
        """Real plagiarism detection with web checking"""
        results = {
            'web_similarity': self._check_web_sources(text),
            'pattern_analysis': self._analyze_patterns(text),
            'overall_score': 0
        }
        
        results['overall_score'] = max(results['web_similarity'], results['pattern_analysis'])
        return results
    
    def _check_web_sources(self, text):
        """Check text against web sources"""
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20][:3]
        max_similarity = 0
        
        for sentence in sentences:
            try:
                # Use DuckDuckGo API for real web search
                query = quote(sentence[:80])
                url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
                
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('Abstract'):
                        similarity = self._text_similarity(sentence, data['Abstract'])
                        max_similarity = max(max_similarity, similarity)
                        
            except:
                continue
                
        return max_similarity
    
    def _analyze_patterns(self, text):
        """Analyze text for plagiarism patterns"""
        # Check for academic plagiarism indicators
        academic_phrases = len(re.findall(r'\b(according to|research shows|studies indicate|it has been found)\b', text, re.IGNORECASE))
        
        # Check for repetitive sentence structures
        sentences = text.split('.')
        sentence_starts = [s.strip().split()[:2] for s in sentences if len(s.strip().split()) >= 2]
        start_counts = Counter([' '.join(start) for start in sentence_starts])
        
        repetition_score = max(start_counts.values()) / max(len(sentences), 1) if start_counts else 0
        academic_score = min(academic_phrases / max(len(text.split()) / 100, 1), 1.0)
        
        return min((repetition_score + academic_score) / 2, 1.0)
    
    def _text_similarity(self, text1, text2):
        """Calculate similarity between two texts"""
        try:
            tfidf = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0

class RealAIDetector:
    def detect_ai_content(self, text):
        """Real AI content detection"""
        features = self._extract_features(text)
        ai_score = self._calculate_ai_probability(features)
        
        return {
            'ai_probability': ai_score,
            'confidence_level': 'High' if ai_score > 0.7 else 'Medium' if ai_score > 0.4 else 'Low',
            'features': features
        }
    
    def _extract_features(self, text):
        """Extract AI detection features"""
        words = text.split()
        sentences = text.split('.')
        
        # Feature 1: Sentence length uniformity
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        length_variance = np.var(sentence_lengths) if sentence_lengths else 0
        uniformity_score = 1 / (1 + length_variance / 10)
        
        # Feature 2: Vocabulary diversity
        unique_words = len(set(words))
        diversity_score = unique_words / max(len(words), 1)
        
        # Feature 3: AI-typical phrases
        ai_phrases = len(re.findall(r'\b(furthermore|moreover|additionally|consequently|it is important to note)\b', text, re.IGNORECASE))
        phrase_density = ai_phrases / max(len(words) / 100, 1)
        
        # Feature 4: Formal language patterns
        formal_patterns = len(re.findall(r'\b(therefore|however|nevertheless|thus|hence)\b', text, re.IGNORECASE))
        formal_density = formal_patterns / max(len(words) / 100, 1)
        
        return {
            'uniformity': uniformity_score,
            'diversity': diversity_score,
            'ai_phrases': min(phrase_density / 3, 1.0),
            'formality': min(formal_density / 2, 1.0)
        }
    
    def _calculate_ai_probability(self, features):
        """Calculate AI probability from features"""
        # Weighted scoring based on AI indicators
        score = (
            features['uniformity'] * 0.3 +
            (1 - features['diversity']) * 0.25 +
            features['ai_phrases'] * 0.25 +
            features['formality'] * 0.2
        )
        
        return min(score, 1.0)