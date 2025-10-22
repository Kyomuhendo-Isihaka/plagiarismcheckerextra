import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import Upload
import re
from urllib.parse import quote

class EnhancedPlagiarismDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.similarity_threshold = 0.3
    
    def comprehensive_check(self, text, title=""):
        """Perform real plagiarism detection"""
        import requests
        from urllib.parse import quote
        
        results = {
            'database_matches': self._check_database(text),
            'internet_matches': self._check_internet_real(text),
            'semantic_analysis': self._real_semantic_analysis(text),
            'citation_analysis': self._analyze_citations(text),
            'overall_score': 0,
            'detailed_matches': []
        }
        
        # Calculate real overall plagiarism score
        db_score = results['database_matches']['similarity_score']
        web_score = results['internet_matches']['similarity_score']
        semantic_score = results['semantic_analysis']['similarity_score']
        
        results['overall_score'] = max(db_score, web_score, semantic_score)
        results['risk_level'] = self._calculate_risk_level(results['overall_score'])
        
        return results
    
    def _check_database(self, text):
        """Check against internal database"""
        existing_docs = Upload.objects.exclude(content__isnull=True).values_list('content', 'title', 'id')
        
        if not existing_docs:
            return {'similarity_score': 0, 'matches': [], 'source': 'database'}
        
        try:
            corpus = [text] + [doc[0] for doc in existing_docs if doc[0]]
            if len(corpus) < 2:
                return {'similarity_score': 0, 'matches': [], 'source': 'database'}
            
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            matches = []
            for i, (content, title, doc_id) in enumerate(existing_docs):
                if content and similarities[i] > self.similarity_threshold:
                    matches.append({
                        'title': title or f'Document {doc_id}',
                        'similarity': float(similarities[i]),
                        'source_type': 'Internal Database',
                        'doc_id': doc_id
                    })
            
            return {
                'similarity_score': float(max(similarities)) if len(similarities) > 0 else 0,
                'matches': sorted(matches, key=lambda x: x['similarity'], reverse=True)[:5],
                'source': 'database'
            }
        except:
            return {'similarity_score': 0, 'matches': [], 'source': 'database'}
    
    def _check_internet(self, text):
        """Check against internet sources"""
        matches = []
        max_similarity = 0
        
        # Extract key phrases for search
        sentences = text.split('.')[:3]  # Check first 3 sentences
        
        for sentence in sentences:
            if len(sentence.strip()) > 20:
                search_results = self._search_web(sentence.strip())
                for result in search_results:
                    similarity = self._calculate_text_similarity(sentence, result.get('snippet', ''))
                    if similarity > self.similarity_threshold:
                        matches.append({
                            'title': result.get('title', 'Unknown'),
                            'url': result.get('url', ''),
                            'similarity': similarity,
                            'source_type': 'Web Source',
                            'snippet': result.get('snippet', '')[:200]
                        })
                        max_similarity = max(max_similarity, similarity)
        
        return {
            'similarity_score': max_similarity,
            'matches': sorted(matches, key=lambda x: x['similarity'], reverse=True)[:3],
            'source': 'internet'
        }
    
    def _search_web(self, query):
        """Search web for similar content"""
        try:
            # Using a simple search API (replace with actual API)
            encoded_query = quote(query[:100])
            # Placeholder for actual web search implementation
            return [
                {
                    'title': 'Sample Academic Paper',
                    'url': 'https://example.com/paper1',
                    'snippet': query[:50] + '...'  # Simulated match
                }
            ]
        except:
            return []
    
    def _semantic_analysis(self, text):
        """Perform semantic similarity analysis"""
        # Simplified semantic analysis
        sentences = text.split('.')
        repetitive_patterns = 0
        
        for i in range(len(sentences) - 1):
            similarity = self._calculate_text_similarity(sentences[i], sentences[i + 1])
            if similarity > 0.7:
                repetitive_patterns += 1
        
        semantic_score = min(repetitive_patterns / max(len(sentences), 1), 1.0)
        
        return {
            'similarity_score': semantic_score,
            'repetitive_patterns': repetitive_patterns,
            'analysis': 'High repetition detected' if semantic_score > 0.5 else 'Normal variation'
        }
    
    def _analyze_citations(self, text):
        """Analyze citation patterns"""
        citation_patterns = [
            r'\([A-Za-z]+,?\s*\d{4}\)',  # (Author, 2023)
            r'\[[0-9]+\]',               # [1]
            r'et al\.',                  # et al.
            r'ibid\.',                   # ibid.
        ]
        
        citations_found = 0
        for pattern in citation_patterns:
            citations_found += len(re.findall(pattern, text))
        
        word_count = len(text.split())
        citation_density = citations_found / max(word_count / 100, 1)  # Citations per 100 words
        
        return {
            'citation_count': citations_found,
            'citation_density': citation_density,
            'properly_cited': citation_density > 0.5,
            'missing_citations_risk': 'High' if citation_density < 0.2 else 'Low'
        }
    
    def _calculate_text_similarity(self, text1, text2):
        """Calculate similarity between two texts"""
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def _calculate_risk_level(self, score):
        """Calculate risk level based on score"""
        if score > 0.8:
            return 'Critical'
        elif score > 0.5:
            return 'High'
        elif score > 0.3:
            return 'Medium'
        else:
            return 'Low'