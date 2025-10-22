"""
AI-generated content detection module
"""
import re
import logging
from collections import Counter
import statistics

logger = logging.getLogger(__name__)

class AIContentDetector:
    """Detect AI-generated content using linguistic patterns"""
    
    def __init__(self):
        # Common AI-generated text patterns
        self.ai_phrases = [
            "as an ai", "i'm an ai", "as a language model", "i don't have personal",
            "i cannot", "i'm not able to", "i don't have the ability",
            "it's worth noting", "it's important to note", "furthermore",
            "in conclusion", "to summarize", "in summary", "overall",
            "however", "nevertheless", "moreover", "additionally",
            "on the other hand", "in contrast", "similarly",
            "for instance", "for example", "such as", "including but not limited to"
        ]
        
        # Repetitive sentence starters common in AI text
        self.repetitive_starters = [
            "the", "this", "it", "in", "for", "with", "by", "on", "at", "to"
        ]
        
        # Academic buzzwords often overused by AI
        self.academic_buzzwords = [
            "comprehensive", "extensive", "significant", "substantial", "considerable",
            "various", "numerous", "multiple", "diverse", "wide range",
            "important", "crucial", "essential", "vital", "critical",
            "effective", "efficient", "successful", "beneficial", "advantageous"
        ]

    def detect_ai_content(self, text):
        """
        Analyze text for AI-generated content indicators
        Returns: dict with detection results
        """
        if not text or len(text.strip()) < 100:
            return {"is_ai_generated": False, "confidence": 0, "indicators": []}
        
        text = text.lower().strip()
        indicators = []
        confidence_score = 0
        
        # Check for direct AI phrases
        ai_phrase_count = self._check_ai_phrases(text)
        if ai_phrase_count > 0:
            indicators.append(f"Contains {ai_phrase_count} AI-specific phrases")
            confidence_score += ai_phrase_count * 20
        
        # Check sentence structure patterns
        repetitive_score = self._check_repetitive_patterns(text)
        if repetitive_score > 0.3:
            indicators.append(f"Repetitive sentence patterns ({repetitive_score:.1%})")
            confidence_score += repetitive_score * 30
        
        # Check for overuse of academic buzzwords
        buzzword_score = self._check_buzzwords(text)
        if buzzword_score > 0.15:
            indicators.append(f"Overuse of academic buzzwords ({buzzword_score:.1%})")
            confidence_score += buzzword_score * 25
        
        # Check sentence length uniformity (AI tends to write uniform sentences)
        uniformity_score = self._check_sentence_uniformity(text)
        if uniformity_score > 0.7:
            indicators.append(f"Uniform sentence lengths ({uniformity_score:.1%})")
            confidence_score += uniformity_score * 20
        
        # Check for lack of personal voice/experience
        personal_score = self._check_personal_voice(text)
        if personal_score < 0.1:
            indicators.append("Lacks personal voice or experience")
            confidence_score += 15
        
        # Cap confidence at 100
        confidence_score = min(confidence_score, 100)
        
        return {
            "is_ai_generated": confidence_score > 50,
            "confidence": confidence_score,
            "indicators": indicators,
            "risk_level": self._get_risk_level(confidence_score)
        }
    
    def _check_ai_phrases(self, text):
        """Count AI-specific phrases"""
        count = 0
        for phrase in self.ai_phrases:
            count += text.count(phrase)
        return count
    
    def _check_repetitive_patterns(self, text):
        """Check for repetitive sentence starting patterns"""
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) < 5:
            return 0
        
        starters = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                first_word = sentence.split()[0] if sentence.split() else ""
                starters.append(first_word.lower())
        
        if not starters:
            return 0
        
        # Calculate repetition ratio
        most_common = Counter(starters).most_common(1)[0][1]
        return most_common / len(starters)
    
    def _check_buzzwords(self, text):
        """Check for overuse of academic buzzwords"""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0
        
        buzzword_count = sum(1 for word in words if word in self.academic_buzzwords)
        return buzzword_count / len(words)
    
    def _check_sentence_uniformity(self, text):
        """Check if sentences are uniformly long (AI characteristic)"""
        sentences = re.split(r'[.!?]+', text)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        
        if len(sentence_lengths) < 5:
            return 0
        
        # Calculate coefficient of variation (lower = more uniform)
        if statistics.mean(sentence_lengths) == 0:
            return 0
        
        cv = statistics.stdev(sentence_lengths) / statistics.mean(sentence_lengths)
        return 1 - cv  # Convert to uniformity score
    
    def _check_personal_voice(self, text):
        """Check for personal pronouns and experiences"""
        personal_indicators = ["i ", "my ", "me ", "myself", "personally", "in my experience"]
        count = sum(text.count(indicator) for indicator in personal_indicators)
        words = len(text.split())
        return count / words if words > 0 else 0
    
    def _get_risk_level(self, confidence):
        """Convert confidence score to risk level"""
        if confidence >= 80:
            return "Very High"
        elif confidence >= 60:
            return "High"
        elif confidence >= 40:
            return "Medium"
        elif confidence >= 20:
            return "Low"
        else:
            return "Very Low"

# Global detector instance
ai_detector = AIContentDetector()