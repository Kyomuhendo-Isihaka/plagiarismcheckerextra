import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import re
import textstat
from collections import Counter

class AdvancedAIDetector:
    def __init__(self):
        self.features = [
            'avg_sentence_length', 'vocabulary_diversity', 'repetition_score',
            'coherence_score', 'complexity_score', 'pattern_regularity',
            'emotional_variance', 'structural_consistency'
        ]
        self.model = self._initialize_model()
    
    def detect_ai_content(self, text):
        """Comprehensive AI detection analysis"""
        features = self._extract_features(text)
        
        # Calculate AI probability using multiple methods
        statistical_prob = self._statistical_analysis(features)
        linguistic_prob = self._linguistic_analysis(text)
        pattern_prob = self._pattern_analysis(text)
        
        # Weighted combination
        ai_probability = (
            statistical_prob * 0.4 +
            linguistic_prob * 0.35 +
            pattern_prob * 0.25
        )
        
        return {
            'ai_probability': float(ai_probability),
            'confidence_level': self._calculate_confidence(ai_probability),
            'feature_analysis': features,
            'detailed_analysis': {
                'statistical_indicators': self._get_statistical_indicators(features),
                'linguistic_patterns': self._get_linguistic_patterns(text),
                'ai_signatures': self._detect_ai_signatures(text)
            },
            'risk_assessment': self._assess_risk(ai_probability)
        }
    
    def _extract_features(self, text):
        """Extract comprehensive features for AI detection"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        words = text.split()
        
        features = {
            'avg_sentence_length': np.mean([len(s.split()) for s in sentences]) if sentences else 0,
            'vocabulary_diversity': len(set(words)) / max(len(words), 1),
            'repetition_score': self._calculate_repetition(text),
            'coherence_score': self._calculate_coherence(sentences),
            'complexity_score': textstat.flesch_reading_ease(text) / 100,
            'pattern_regularity': self._calculate_pattern_regularity(sentences),
            'emotional_variance': self._calculate_emotional_variance(text),
            'structural_consistency': self._calculate_structural_consistency(sentences)
        }
        
        return features
    
    def _statistical_analysis(self, features):
        """Statistical analysis for AI detection"""
        # AI-generated text typically shows specific statistical patterns
        ai_indicators = 0
        
        # Check for AI-typical patterns
        if features['avg_sentence_length'] > 15 and features['avg_sentence_length'] < 25:
            ai_indicators += 0.2  # AI tends to generate medium-length sentences
        
        if features['vocabulary_diversity'] < 0.6:
            ai_indicators += 0.15  # AI often has lower vocabulary diversity
        
        if features['pattern_regularity'] > 0.7:
            ai_indicators += 0.25  # AI shows high pattern regularity
        
        if features['structural_consistency'] > 0.8:
            ai_indicators += 0.2  # AI maintains consistent structure
        
        if features['emotional_variance'] < 0.3:
            ai_indicators += 0.2  # AI often lacks emotional variation
        
        return min(ai_indicators, 1.0)
    
    def _linguistic_analysis(self, text):
        """Linguistic pattern analysis"""
        ai_patterns = [
            r'\b(furthermore|moreover|additionally|consequently)\b',  # Formal connectors
            r'\b(it is important to note|it should be noted)\b',      # AI phrases
            r'\b(in conclusion|to summarize|overall)\b',             # Summary phrases
            r'\b(various|numerous|several|multiple)\b',              # Vague quantifiers
        ]
        
        pattern_matches = 0
        for pattern in ai_patterns:
            pattern_matches += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Normalize by text length
        pattern_density = pattern_matches / max(len(text.split()) / 100, 1)
        
        return min(pattern_density / 5, 1.0)  # Normalize to 0-1
    
    def _pattern_analysis(self, text):
        """Analyze structural and stylistic patterns"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Check for repetitive sentence structures
        sentence_starts = [s.split()[:2] for s in sentences if len(s.split()) >= 2]
        start_patterns = Counter([' '.join(start) for start in sentence_starts])
        
        # High repetition in sentence starts indicates AI
        max_repetition = max(start_patterns.values()) if start_patterns else 0
        repetition_score = min(max_repetition / max(len(sentences), 1), 1.0)
        
        # Check for uniform paragraph structure
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            para_lengths = [len(p.split()) for p in paragraphs if p.strip()]
            length_variance = np.var(para_lengths) if para_lengths else 0
            uniformity_score = 1 / (1 + length_variance / 100)  # Higher variance = lower AI probability
        else:
            uniformity_score = 0.5
        
        return (repetition_score * 0.6 + uniformity_score * 0.4)
    
    def _calculate_repetition(self, text):
        """Calculate text repetition score"""
        words = text.lower().split()
        word_freq = Counter(words)
        
        # Calculate repetition based on word frequency distribution
        total_words = len(words)
        unique_words = len(set(words))
        
        if total_words == 0:
            return 0
        
        repetition = 1 - (unique_words / total_words)
        return repetition
    
    def _calculate_coherence(self, sentences):
        """Calculate text coherence score"""
        if len(sentences) < 2:
            return 0.5
        
        # Simple coherence based on sentence length consistency
        lengths = [len(s.split()) for s in sentences]
        length_variance = np.var(lengths)
        
        # Lower variance indicates higher coherence (AI-like)
        coherence = 1 / (1 + length_variance / 10)
        return coherence
    
    def _calculate_pattern_regularity(self, sentences):
        """Calculate pattern regularity in text structure"""
        if not sentences:
            return 0
        
        # Analyze sentence structure patterns
        structures = []
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 0:
                # Simple structure: short/medium/long
                if len(words) < 8:
                    structures.append('short')
                elif len(words) < 15:
                    structures.append('medium')
                else:
                    structures.append('long')
        
        # Calculate pattern regularity
        structure_counts = Counter(structures)
        if not structure_counts:
            return 0
        
        # High regularity indicates AI generation
        max_pattern = max(structure_counts.values())
        regularity = max_pattern / len(structures)
        
        return regularity
    
    def _calculate_emotional_variance(self, text):
        """Calculate emotional variance in text"""
        # Simple emotional indicators
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'poor']
        neutral_words = ['okay', 'fine', 'adequate', 'reasonable', 'standard', 'normal']
        
        words = text.lower().split()
        
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        neu_count = sum(1 for word in words if word in neutral_words)
        
        total_emotional = pos_count + neg_count + neu_count
        
        if total_emotional == 0:
            return 0.5  # Neutral variance
        
        # Calculate variance in emotional content
        emotions = [pos_count, neg_count, neu_count]
        variance = np.var(emotions) / max(total_emotional, 1)
        
        return variance
    
    def _calculate_structural_consistency(self, sentences):
        """Calculate structural consistency across sentences"""
        if len(sentences) < 3:
            return 0.5
        
        # Analyze punctuation patterns
        punct_patterns = []
        for sentence in sentences:
            commas = sentence.count(',')
            semicolons = sentence.count(';')
            colons = sentence.count(':')
            punct_patterns.append((commas, semicolons, colons))
        
        # Calculate consistency in punctuation usage
        if not punct_patterns:
            return 0.5
        
        # High consistency indicates AI generation
        pattern_variance = np.var([sum(p) for p in punct_patterns])
        consistency = 1 / (1 + pattern_variance)
        
        return consistency
    
    def _initialize_model(self):
        """Initialize a simple model for AI detection"""
        # Placeholder for a trained model
        return RandomForestClassifier(n_estimators=10, random_state=42)
    
    def _calculate_confidence(self, probability):
        """Calculate confidence level"""
        if probability > 0.8:
            return 'Very High'
        elif probability > 0.6:
            return 'High'
        elif probability > 0.4:
            return 'Medium'
        else:
            return 'Low'
    
    def _get_statistical_indicators(self, features):
        """Get statistical indicators for AI detection"""
        return {
            'sentence_uniformity': 'High' if features['pattern_regularity'] > 0.7 else 'Normal',
            'vocabulary_limitation': 'Detected' if features['vocabulary_diversity'] < 0.6 else 'Normal',
            'structural_rigidity': 'High' if features['structural_consistency'] > 0.8 else 'Normal'
        }
    
    def _get_linguistic_patterns(self, text):
        """Get linguistic pattern analysis"""
        formal_phrases = len(re.findall(r'\b(furthermore|moreover|additionally)\b', text, re.IGNORECASE))
        ai_phrases = len(re.findall(r'\b(it is important to note|it should be noted)\b', text, re.IGNORECASE))
        
        return {
            'formal_connectors': formal_phrases,
            'ai_typical_phrases': ai_phrases,
            'pattern_density': (formal_phrases + ai_phrases) / max(len(text.split()) / 100, 1)
        }
    
    def _detect_ai_signatures(self, text):
        """Detect specific AI generation signatures"""
        signatures = []
        
        # Check for repetitive paragraph structures
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 2:
            para_starts = [p.split()[:3] for p in paragraphs if len(p.split()) >= 3]
            if len(set([' '.join(start) for start in para_starts])) < len(para_starts) * 0.8:
                signatures.append('Repetitive paragraph openings')
        
        # Check for excessive use of transition words
        transitions = len(re.findall(r'\b(however|therefore|furthermore|moreover|consequently|additionally)\b', text, re.IGNORECASE))
        if transitions > len(text.split()) / 50:  # More than 2% transition words
            signatures.append('Excessive transition words')
        
        # Check for lack of personal pronouns (AI tends to avoid first person)
        personal_pronouns = len(re.findall(r'\b(I|me|my|mine|myself)\b', text, re.IGNORECASE))
        if personal_pronouns < len(text.split()) / 200:  # Less than 0.5% personal pronouns
            signatures.append('Lack of personal voice')
        
        return signatures
    
    def _assess_risk(self, probability):
        """Assess risk level based on AI probability"""
        if probability > 0.8:
            return {
                'level': 'Critical',
                'description': 'Very high likelihood of AI generation',
                'recommendation': 'Manual review required'
            }
        elif probability > 0.6:
            return {
                'level': 'High',
                'description': 'High likelihood of AI generation',
                'recommendation': 'Further investigation recommended'
            }
        elif probability > 0.4:
            return {
                'level': 'Medium',
                'description': 'Moderate AI indicators present',
                'recommendation': 'Monitor for additional signs'
            }
        else:
            return {
                'level': 'Low',
                'description': 'Low likelihood of AI generation',
                'recommendation': 'Likely human-authored content'
            }