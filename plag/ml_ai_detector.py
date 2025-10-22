"""
Machine Learning-powered AI content detection
"""
import re
import numpy as np
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class MLAIDetector:
    def __init__(self):
        # Pre-trained patterns (in production, use actual ML model)
        self.ai_patterns = {
            'transition_words': [
                'furthermore', 'moreover', 'additionally', 'consequently', 
                'nevertheless', 'nonetheless', 'therefore', 'thus', 'hence'
            ],
            'formal_phrases': [
                'it is important to note', 'it should be emphasized', 
                'it is worth mentioning', 'one must consider', 'it is evident that'
            ],
            'ai_markers': [
                'as an ai', 'i am an ai', 'as a language model', 'i cannot', 
                'i don\'t have personal', 'i\'m not able to'
            ],
            'repetitive_starters': [
                'the', 'this', 'it', 'in', 'for', 'with', 'by', 'on', 'at'
            ]
        }
        
        # Weights for different features (trained values)
        self.feature_weights = {
            'sentence_uniformity': 0.25,
            'transition_density': 0.20,
            'vocabulary_diversity': 0.15,
            'punctuation_patterns': 0.10,
            'paragraph_structure': 0.15,
            'ai_markers': 0.15
        }
    
    def extract_features(self, text):
        """Extract ML features from text"""
        features = {}
        
        # Sentence analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 3:
            return {'confidence': 0, 'features': {}}
        
        # Feature 1: Sentence length uniformity
        sentence_lengths = [len(s.split()) for s in sentences]
        if sentence_lengths:
            length_std = np.std(sentence_lengths)
            length_mean = np.mean(sentence_lengths)
            uniformity_score = 1 - (length_std / (length_mean + 1))
            features['sentence_uniformity'] = max(0, min(1, uniformity_score))
        
        # Feature 2: Transition word density
        text_lower = text.lower()
        transition_count = sum(text_lower.count(word) for word in self.ai_patterns['transition_words'])
        word_count = len(text.split())
        features['transition_density'] = min(1, transition_count / (word_count / 100))
        
        # Feature 3: Vocabulary diversity (Type-Token Ratio)
        words = re.findall(r'\b\w+\b', text.lower())
        unique_words = set(words)
        if words:
            features['vocabulary_diversity'] = 1 - (len(unique_words) / len(words))
        
        # Feature 4: Punctuation patterns
        punctuation_count = len(re.findall(r'[,;:()]', text))
        features['punctuation_patterns'] = min(1, punctuation_count / (word_count / 50))
        
        # Feature 5: Paragraph structure uniformity
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            para_lengths = [len(p.split()) for p in paragraphs if p.strip()]
            if para_lengths:
                para_std = np.std(para_lengths)
                para_mean = np.mean(para_lengths)
                para_uniformity = 1 - (para_std / (para_mean + 1))
                features['paragraph_structure'] = max(0, min(1, para_uniformity))
        
        # Feature 6: Direct AI markers
        ai_marker_count = sum(text_lower.count(marker) for marker in self.ai_patterns['ai_markers'])
        features['ai_markers'] = min(1, ai_marker_count * 0.5)
        
        return features
    
    def predict_ai_content(self, text):
        """ML-based AI content prediction"""
        features = self.extract_features(text)
        
        if not features:
            return {
                'is_ai_generated': False,
                'confidence': 0,
                'ml_score': 0,
                'feature_analysis': {},
                'indicators': []
            }
        
        # Calculate weighted score
        ml_score = 0
        feature_analysis = {}
        indicators = []
        
        for feature_name, value in features.items():
            if feature_name in self.feature_weights:
                weight = self.feature_weights[feature_name]
                contribution = value * weight
                ml_score += contribution
                
                feature_analysis[feature_name] = {
                    'value': round(value, 3),
                    'weight': weight,
                    'contribution': round(contribution, 3)
                }
                
                # Add indicators for high-scoring features
                if value > 0.6:
                    indicators.append(f"High {feature_name.replace('_', ' ')}: {value:.1%}")
        
        # Convert to percentage
        confidence = min(100, ml_score * 100)
        
        # Additional pattern-based indicators
        text_lower = text.lower()
        
        # Check for AI-specific patterns
        if any(marker in text_lower for marker in self.ai_patterns['ai_markers']):
            confidence += 20
            indicators.append("Contains AI self-identification phrases")
        
        # Check for excessive formal language
        formal_count = sum(text_lower.count(phrase) for phrase in self.ai_patterns['formal_phrases'])
        if formal_count > 2:
            confidence += 10
            indicators.append(f"Excessive formal phrases ({formal_count} instances)")
        
        # Check repetitive sentence starters
        sentences = re.split(r'[.!?]+', text)
        starters = [s.strip().split()[0].lower() for s in sentences if s.strip() and s.strip().split()]
        starter_freq = Counter(starters)
        most_common_freq = starter_freq.most_common(1)[0][1] if starter_freq else 0
        
        if most_common_freq > len(sentences) * 0.3:
            confidence += 15
            indicators.append(f"Repetitive sentence starters ({most_common_freq}/{len(sentences)} sentences)")
        
        confidence = min(100, confidence)
        
        return {
            'is_ai_generated': confidence > 60,
            'confidence': round(confidence, 1),
            'ml_score': round(ml_score, 3),
            'feature_analysis': feature_analysis,
            'indicators': indicators,
            'risk_level': self._get_risk_level(confidence)
        }
    
    def _get_risk_level(self, confidence):
        if confidence >= 85:
            return "Very High"
        elif confidence >= 70:
            return "High"
        elif confidence >= 50:
            return "Medium"
        elif confidence >= 30:
            return "Low"
        else:
            return "Very Low"

# Global ML detector instance
ml_ai_detector = MLAIDetector()